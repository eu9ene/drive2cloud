import os.path
import logging

from index.file_index import FileIndex
from read.file_reader import LocalFileReader
from read.ftp_reader import FtpReader
from settings import CommonSettings
from upload.dropbox_uploader import DropboxUploader


class App:
    def __init__(self, reindex):
        self.reindex = reindex
        self.reader = None
        self.uploader = None
        self.index = None

    def run(self):
        try:
            self.reader = self.create_reader(CommonSettings.READER_TYPE)
            self.uploader = self.create_uploader(CommonSettings.UPLOADER_TYPE)
            self.index = self.load_index(CommonSettings.FILE_INDEX)

            logging.info('Start uploading process')
            self.upload()
            logging.info('Completed.')
        except Exception as ex:
            logging.exception(ex)
        finally:
            if self.index:
                self.index.save()
            if self.uploader:
                self.uploader.close()
            if self.reader:
                self.reader.close()

    def load_index(self, file):
        if not self.reindex and os.path.isfile(file):
            index = FileIndex.load(file)
            logging.info('index was loaded from file')
        else:
            logging.info('building initial index')
            index = FileIndex(file)

            counter = 0
            for file_path in self.uploader.list_files():
                index.add(file_path)
                counter += 1

            index.save()
            logging.info(f'index building completed. {counter} files were added to index')

        return index

    def upload(self):
        def upload_file(file_retriever):
            if self.index.contains(file_retriever.path):
                return
            self.uploader.upload_file(file_retriever)
            self.index.add(file_retriever.path)

        self.reader.retrieve_files(upload_file)
        self.index.save()

    @staticmethod
    def create_reader(type):
        if type == 'ftp':
            from settings import FtpSettings
            return FtpReader(FtpSettings.FTP_HOST,
                             FtpSettings.FTP_PATH,
                             FtpSettings.FTP_LOGIN,
                             FtpSettings.FTP_PWD,
                             FtpSettings.FTP_ENCODING)
        elif type == 'local':
            from settings import LocalSettings
            return LocalFileReader(LocalSettings.LOCAL_ROOT_DIR)

        raise ValueError('not supported reader: ' + type)

    @staticmethod
    def create_uploader(type):
        if type == 'dropbox':
            from settings import DropboxSettings
            return DropboxUploader(DropboxSettings.DROPBOX_TOKEN,
                                   DropboxSettings.DROPBOX_PATH)

        raise ValueError('not supported uploader: ' + type)
