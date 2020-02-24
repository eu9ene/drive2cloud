from typing import Iterable

from read.reader import FileRetriever


class CloudUploader:
    def __init__(self):
        pass

    def list_files(self) -> Iterable[str]:
        """ Lists all file paths in the root directory """
        pass

    def upload_file(self, file_retriever: FileRetriever):
        """ Uploads file to the cloud, reading it with :file_retriever """
        pass

    def close(self):
        pass
