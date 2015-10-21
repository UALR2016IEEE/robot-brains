import time


class Base:
    def __init__(self, cid: {str, type(None)}=None):
        pass

    def acquire_align(self) -> bool:
        start_time = time.time()
        aligning = True
        confidence = 0.0
        lidar_data = yield
        while aligning:
            find_victim()
            instruct_mobility()
            confidence = 1.0
            aligning = confidence < 0.9
            lidar_data = yield False
        yield True

    def attempt_recover(self) -> bool:
        return
