import pickle
from os import path


class FileIndex:
    def __init__(self, file_path):
        self._file_path = file_path
        self._index = dict()

    @classmethod
    def load(cls, file_path):
        file_index = cls(file_path)

        with open(file_path, 'rb') as file:
            file_index._index = pickle.load(file)

        return file_index

    def contains(self, file_path):
        file_path = file_path.lower()
        directory, name = path.split(file_path)
        dir_set = self._index.get(directory, None)
        if dir_set is None:
            return False
        return name in dir_set

    def add(self, file_path):
        file_path = file_path.lower()
        directory, name = path.split(file_path)
        dir_set = self._index.get(directory, None)

        if dir_set is None:
            dir_set = set()
            self._index[directory] = dir_set

        dir_set.add(name)

    def save(self):
        with open(self._file_path, 'wb') as file:
            pickle.dump(self._index, file)
