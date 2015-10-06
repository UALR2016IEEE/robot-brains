import numpy as np


class Base:
    def __init__(self):
        self._load_map()

    def _load_map(self):
        pass

    def scan(self) -> np.ndarray:
        pass
