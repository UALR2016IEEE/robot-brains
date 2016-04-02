from contextlib import contextmanager
import struct
import serial
import time

try:
    import wiringpi2 as wiringpi
except ImportError:
    wired_mode = False
else:
    wired_mode = True

if wired_mode:
    OUTPUT = 1
    INPUT = 0
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
        raise NotImplementedError

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

class RPStatusClass(StatusClass):
    @contextmanager
    def UART_mux(self):
        wiringpi.digitalWrite(MUX_PIN, 1)
        try:
            yield
        finally:
            wiringpi.digitalWrite(MUX_PIN, 0)



if wired_mode:
    status = RPStatusClass("/dev/ttyUSB0")
else:
    status = StatusClass("COM7")
status.baudrate = 115200
status.timeout = 0.5
time.sleep(2)


