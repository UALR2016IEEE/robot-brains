import serial
import time
from multiprocessing import Lock
import asyncio


class StatusClass(serial.Serial):
    def __init__(self, *args, **kwargs):
        self.lock = Lock()
        super(StatusClass, self).__init__(*args, **kwargs)

status = StatusClass("/dev/ttyUSB0")
status.baudrate = 115200
status.timeout = 0.1
time.sleep(2)


