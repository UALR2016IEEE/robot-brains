import time


class Base:
    def __init__(self, cid: {str, type(None)}=None):
        pass

    def aquire_align(self) -> bool:
        start_time = time.time()
        aligning = True
        confindence = 0.0
        lidar_data = yield
        while aligning:
            find_victim()
            instruct_mobility()
            confindence = 1.0
            aligning = confindence < 0.9
            lidar_data = yield False
        yield True

    def attempt_recover(self) -> bool:
        return
