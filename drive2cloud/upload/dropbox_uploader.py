import io
import logging

import requests
from dropbox import dropbox
from dropbox.exceptions import ApiError, AuthError
from dropbox.files import UploadSessionCursor, CommitInfo, WriteMode, FileMetadata
from tenacity import retry, stop_after_attempt, retry_if_exception_type, after_log

from read.ftp_reader import FileRetriever
from upload.uploader import CloudUploader

MAX_CHUNK_SIZE = 10 * 1024 * 1024


class DropboxUploader(CloudUploader):
    def __init__(self, token, directory):
        super().__init__()
        self._directory = directory
        self._dbx = dropbox.Dropbox(token, timeout=120)
        self._validate_token()

        logging.info('Dropbox client initialized')

    def _validate_token(self):
        try:
            self._dbx.users_get_current_account()
        except AuthError as err:
            logging.error(err)
            raise ValueError("Invalid access token; try re-generating an "
                             "access token from the app console on the web.")

    def list_files(self):
        result = self._dbx.files_list_folder(self._directory, recursive=True)

        while True:
            for entry in result.entries:
                if isinstance(entry, FileMetadata):
                    yield entry.path_lower

            if not result.has_more:
                break

            result = self._dbx.files_list_folder_continue(result.cursor)

    def upload_file(self, file_retriever: FileRetriever):
        logging.info(f"Uploading {file_retriever.path} to Dropbox ...")

        try:
            upload_path = self._directory + '/' + file_retriever.path
            uploader = FileUploader(file_retriever, upload_path, self._dbx)

            if file_retriever.size > MAX_CHUNK_SIZE:
                uploader.upload_in_chunks(MAX_CHUNK_SIZE)
            else:
                uploader.upload()

            logging.info(f"Uploaded: {file_retriever.path}")
        except ApiError as err:
            if err.error.is_path() and err.error.get_path().error.is_insufficient_space():
                logging.error("ERROR: Cannot upload; insufficient space.")
                raise
            elif err.user_message_text:
                logging.error(err.user_message_text)
                raise
            else:
                raise

        assert uploader.total_bytes == file_retriever.size


class FileUploader:
    UPLOAD_RETRY_COUNT = 5

    def __init__(self, file_retriever, upload_path, dbx):
        self._dbx = dbx
        self._upload_path = upload_path
        self._file_retriever = file_retriever
        self._buffer = io.BytesIO()
        self._total_bytes = 0
        self._session = None

    @property
    def total_bytes(self):
        return self._total_bytes

    @retry(stop=stop_after_attempt(UPLOAD_RETRY_COUNT),
           retry=retry_if_exception_type(requests.exceptions.ReadTimeout),
           after=after_log(logging.getLogger(), logging.WARNING))
    def upload(self):
        self._file_retriever.read(self._buffer.write)
        bytes = self._buffer.getvalue()
        assert self._total_bytes + len(bytes) == self._file_retriever.size

        self._dbx.files_upload(bytes,
                               path=self._upload_path,
                               mode=WriteMode('overwrite'),
                               client_modified=self._file_retriever.modified)
        self._total_bytes += len(bytes)

    def upload_in_chunks(self, chunk_size):
        self._file_retriever.read(lambda data: self._on_read(data, chunk_size))
        assert self._session is not None

        bytes = self._buffer.getvalue()
        assert self._total_bytes + len(bytes) == self._file_retriever.size

        self._upload_session(bytes, finish=True)

        self._total_bytes += len(bytes)
        logging.info('chunk %s bytes uploaded. upload finished, total: %s bytes' % (len(bytes), self._total_bytes))

    def _on_read(self, data, chunk_size):
        self._buffer.write(data)

        if self._buffer.tell() > chunk_size:
            bytes = self._buffer.getvalue()

            self._upload_session(bytes, finish=False)

            self._total_bytes += len(bytes)
            logging.info('chunk %s bytes uploaded, total: %s bytes' % (len(bytes), self._total_bytes))
            self._buffer.truncate(0)
            self._buffer.seek(0)

    @retry(stop=stop_after_attempt(UPLOAD_RETRY_COUNT),
           retry=retry_if_exception_type(requests.exceptions.ReadTimeout),
           after=after_log(logging.getLogger(), logging.WARNING))
    def _upload_session(self, bytes, finish):
        if self._session is None:
            start_result = self._dbx.files_upload_session_start(bytes)
            self._session = start_result.session_id
        elif finish:
            cursor = UploadSessionCursor(self._session, self._total_bytes)
            info = CommitInfo(path=self._upload_path,
                              mode=WriteMode('overwrite'),
                              client_modified=self._file_retriever.modified)
            self._dbx.files_upload_session_finish(bytes, cursor, info)
        else:
            cursor = UploadSessionCursor(self._session, self._total_bytes)
            self._dbx.files_upload_session_append_v2(bytes, cursor)
