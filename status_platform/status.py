from contextlib import contextmanager
import serial
import time

import wiringpi2 as wiringpi
from wiringpi2 import INPUT, OUTPUT
pi_rev = wiringpi.piBoardRev()
wiringpi.wiringPiSetupPhys()
MUX_PIN = 7
wiringpi.setPinMode(MUX_PIN, OUTPUT)
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
            self.write("5")
        else:
            self.write("2")

    def rail(self, lower=False):
        if lower:
            self.write("6")
        else:
            self.write("7")




status = StatusClass("/dev/ttyUSB0")
status.baudrate = 115200
status.timeout = 0.2
time.sleep(2)


