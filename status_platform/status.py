import serial
from multiprocessing import Lock
import asyncio

ard = serial.Serial("/dev/ttyUSB0")
ard.buadrate = 155200

lock = Lock()

def line(len, angle):
    with lock:
        ard.write(b"L{:4d}{:-1.3f}".format(len, angle))

def rotate(angle):
    line(0, angle)

def arm(enable):
    ard.write(b"E{:1d}".format(enable))