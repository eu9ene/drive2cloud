import logging
import os
from datetime import datetime
from stat import UF_HIDDEN

from read.reader import DriveReader, FileRetriever

CHUNK_SIZE = 128 * 1024


class LocalFileReader(DriveReader):
    def __init__(self, directory):
        super().__init__(directory)

    def retrieve_files(self, callback):
        for path, _, files in os.walk(self.directory):
            for name in files:
                # skip system files
                if name.startswith('.'):
                    continue

                file_path = os.path.join(path, name)

                # detect hidden files on MacOS X
                if (os.stat(file_path).st_flags & UF_HIDDEN) == UF_HIDDEN:
                    continue

                modified = datetime.fromtimestamp(os.path.getmtime(file_path))
                size = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, self.directory)

                retriever = LocalFileRetriever(relative_path, modified, size, file_path)
                callback(retriever)


class LocalFileRetriever(FileRetriever):
    def __init__(self, path, modified, size, os_path):
        super().__init__(path, modified, size)
        self.os_path = os_path

    def read(self, callback):
        logging.info(f'reading {self.os_path} from file system')

        with open(self.os_path, mode='rb') as file:
            while True:
                data = file.read(CHUNK_SIZE)
                if not data:
                    break

                callback(data)
