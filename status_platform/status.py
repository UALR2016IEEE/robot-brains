from contextlib import contextmanager
import struct
import serial
import time

import wiringpi2 as wiringpi
INPUT = 1
OUTPUT = 0
pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupPhys()
MUX_PIN = 7
wiringpi.pinMode(MUX_PIN, OUTPUT)
wiringpi.digitalWrite(MUX_PIN, 0)

class StatusClass(serial.Serial):
    def __init__(self, *args, **kwargs):
        self.lock = None
        super(StatusClass, self).__init__(*args, **kwargs)

    @contextmanager
    def UART_mux(self):
        wiringpi2.digitalWrite(MUX_PIN, 1)
        try:
            yield
        finally:
            wiringpi.digitalWrite(MUX_PIN, 0)

    def claw(self, open=False):
        if open:
            self.write(b"5")
        else:
            self.write(b"2")

    def rail(self, lower=False):
        if lower:
            self.write(b"6")
        else:
            self.write(b"7")

    def button_state(self):
        self.write(b'b')
        state, = struct.unpack('>?', self.read())
        return state


status = StatusClass("/dev/ttyUSB0")
status.baudrate = 115200
status.timeout = 0.5
time.sleep(2)


