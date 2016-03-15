import time


class Base(object):
    def __init__(self, cid: {str, type(None)} = None):
        pass

    def acquire_align(self) -> bool:
        start_time = time.time()
        aligning = True
        confidence = 0.0
        lidar_data = yield
        while aligning:
            self.find_victim()
            self.instruct_mobility()
            confidence = 1.0
            aligning = confidence < 0.9
            lidar_data = yield False
        yield True

    def attempt_recover(self) -> bool:
        return True

    def find_victim(self):
        pass

    def instruct_mobility(self):
        pass

