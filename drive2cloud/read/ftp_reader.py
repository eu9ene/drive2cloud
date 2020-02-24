import logging
from datetime import datetime
from ftplib import FTP

from read.reader import FileRetriever, DriveReader


class FtpReader(DriveReader):
    def __init__(self, host, directory, login='', pwd='', encoding=None):
        super().__init__(directory)
        self._ftp = FTP(host)
        self._ftp.login(login, pwd)

        if encoding is not None:
            self._ftp.encoding = encoding

        self._ftp.cwd(directory)

        logging.info('FTP client initialized')

    def retrieve_files(self, callback):
        self._retrieve_files(self.directory, callback)

    def _retrieve_files(self, directory, callback):
        files = self._ftp.mlsd(directory)

        for file in files:
            file_type = file[1]['type']
            name = file[0]
            if file_type == 'dir':
                self._retrieve_files(directory + '/' + name, callback)
            elif file_type == 'file':
                if name.startswith('.'):  # skip system files
                    continue
                size = int(file[1]['size'])
                modified = file[1]['modify']
                modified_dt = datetime.strptime(modified, "%Y%m%d%H%M%S")
                file_path = directory + '/' + name

                callback(FtpFileRetriever(file_path, modified_dt, size, self._ftp))

    def close(self):
        self._ftp.close()


class FtpFileRetriever(FileRetriever):
    def __init__(self, path, modified, size, ftp):
        super().__init__(path, modified, size)
        self._ftp = ftp

    def read(self, callback):
        logging.info(f'downloading {self.path} from FTP server')
        self._ftp.retrbinary('RETR ' + self.path, callback)
