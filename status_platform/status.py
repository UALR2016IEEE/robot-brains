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

    def prepare_pickup(self):
        self.write(b"8")
        self._wait_until()
        if self.read(1) != b"8":
            raise serial.SerialTimeoutException()

    def pickup(self):
        self.write(b"7")
        self._wait_until()
        if self.read(1) != b"7":
            raise serial.SerialException()
        

    def let_down(self):
        self.write(b"6")
        self._wait_until()
        if self.read(1) != b"6":
            raise serial.SerialException()

    def button_state(self):
        self.write(b'b')
        state, = struct.unpack('>?', self.read())
        return state

    def _wait_until(self, tmo=6):
        start = time.time()
        while not self.inWaiting():
            if time.time() - start > tmo:
                raise serial.SerialTimeoutException()
        return

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


