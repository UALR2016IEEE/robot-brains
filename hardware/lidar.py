__author__ = 'StaticVOiDance'

import numpy as np

class _BaseLidar:
    def __init__(self):
        self._load_map()

    def _load_map(self):
        pass

    def scan(self) -> np.ndarray
        pass
