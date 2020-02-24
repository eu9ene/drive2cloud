from typing import Callable


class FileRetriever:
    def __init__(self, path, modified, size):
        self.path = path
        self.size = size
        self.modified = modified

    def read(self, callback: Callable[[bytes], None]):
        """ Reads block of file data, passes it to callback """
        pass


class DriveReader:
    def __init__(self, directory):
        self.directory = directory

    def retrieve_files(self, callback: Callable[[FileRetriever], None]):
        """ Reads files from directory, passes :FileRetriever to callback for each file """
        pass

    def close(self):
        pass
