import pickle
import numpy as np
from mlp import DEFAULT_SEED


class DataProvider(object):

    def __init__(self, file, shuffle_factor=1, seed=DEFAULT_SEED):
        self.file = open(file, "rb")
        self.shuffle_factor = shuffle_factor
        np.random.seed = seed

    def get_map(self):
        objs = []
        for _ in range(self.shuffle_factor):
            try:
                objs.append(pickle.load(self.file))
            except EOFError:
                self.file.close()
                break
        return objs[np.random.randint(low=0, high=len(objs)-1)]

    def __del__(self):
        self.file.close()


class DataSaver(object):

    def __init__(self, file):
        self.file = open(self.file, "wb")

    def save_map(self, data_map):
        pickle.dump(data_map, self.file)
        self.file.close()

    def __del__(self):
        self.file.close()
