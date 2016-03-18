import time
import serial
import struct
from hardware.robo_claw import constants


class CommandNotReceived(Exception):
    pass


class ChecksumError(Exception):
    pass


class RoboClaw:
    def __init__(self, serial_port: serial.Serial, address):
        self.port = serial_port
        self._crc = 0
        self.address = address

    def write(self, data):
        self.port.write([22])
        sent_data = struct.pack(">B{}s".format(len(data)), self.address, data)
        self.port.write(sent_data)
        return sent_data

    def read(self, length):
        return self.port.read(length)


    def send_command(self, command):
        sent_data = self.write(command)
        crc = self.checksum(sent_data)
        self.port.write(struct.pack(">H", crc))
        self.port.write([22])
        raw_return_code =  self.read(1)
        return_code, = struct.unpack(">B", raw_return_code)
        if return_code != 0xFF:
            raise CommandNotReceived()

    def ask(self, command, length):
        sent_data = self.write(struct.pack(">B", command))
        self.port.write([22])
        fulldata = self.read(length)
        data, checksum = struct.unpack(">{}sH".format(length-2), fulldata)
        check = self.checksum(list(sent_data + data))
        if check != checksum:
            raise ChecksumError()
        return data

    def checksum(self, data):
        # Calculates CRC16 of nBytes of data in byte array message
        # crc16(unsigned char *packet, int nBytes) {
        crc = 0
        for byte in data:
            crc ^= byte << 8
            for bit in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
        return crc & 0xFFFF

    def get_temps(self):
        raw_data = self.ask(constants.GETTEMP, 4)
        temp1_in_tenths, = struct.unpack(">H", raw_data)
        temp1 = temp1_in_tenths * 0.1
        rawdata = self.ask(constants.GETTEMP2, 4)
        temp2_in_tenths, = struct.unpack(">H", raw_data)
        temp2 = temp2_in_tenths * 0.1
        return temp1, temp2

    def get_main_voltage(self):
        rawdata = self.ask(constants.GETMBATT, 4)
        main_voltage_n_tenths, = struct.unpack(">H", rawdata)
        main_voltage = main_voltage_n_tenths * 0.1
        return main_voltage

    def get_motor_currents(self):
        rawdata = self.ask(constants.GETCURRENTS, 6)
        motor1_current_in_ma, motor2_current_in_ma = struct.unpack(">HH", rawdata)
        motor1_current = motor1_current_in_ma / 100
        motor2_current = motor2_current_in_ma /100
        return motor1_current, motor2_current

    def set_motor_positions(self, accel, m1, m2, buffered=False):
        raw_data = struct.pack(">BIiIiI?", constants.MIXEDSPEEDACCELDIST, 12000, *m1, *m2, not buffered)
        self.send_command(raw_data)

    def set_m1_position(self, accel, speed, position, buffer=False):
        raw_data = struct.pack(
            ">BIiI?",
            constants.M1SPEEDACCELDIST,
            accel,
            speed,
            position,
            not buffer
        )
        self.send_command(raw_data)

    def set_m2_position(self, accel, speed, position, buffer=False):
        raw_data = struct.pack(
            ">BIiI?",
            constants.M2SPEEDACCELDIST,
            accel,
            speed,
            position,
            not buffer
        )
        self.send_command(raw_data)

    def set_motor_pwm(self, m1, m2):
        if (1 < m1 < -1) or (1 < m2 < -1):
            raise ValueError("Must be percent duty")
        m1_raw = int(m1 * 32768)
        m2_raw = int(m2 * 32768)
        raw_data = struct.pack(">Bhh",
                               constants.MIXEDDUTY,
                               m1_raw,
                               m2_raw
                               )
        self.send_command(raw_data)

    def reset_motor_positions(self):
        self.send_command(bytes([constants.RESETENC]))

    def get_motor_positions(self):
        # Recive Format:
        # [Enc1(4 bytes),
        # Status(1 bytes),
        # CRC(2 bytes)]

        # Status Codes:
        raw_data = self.ask(constants.GETM1ENC, 7)
        struct_formatter = ">iB"
        m1_position_unsigned, status = struct.unpack(struct_formatter, raw_data)
        underflow = status & 0b00000001
        overflow =  status & 0b00000100
        direction = status & 0b00000010
        m1_position = direction * -1 * m1_position_unsigned
        # if underflow or overflow:
        #     raise OverflowError

        raw_data = self.ask(constants.GETM2ENC, 7)
        m2_position_unsigned, status = struct.unpack(struct_formatter, raw_data)
        underflow = status & 0b00000001
        overflow =  status & 0b00000100
        direction = status & 0b00000010
        m2_position = direction * -1 * m2_position_unsigned
        # if underflow or overflow:
        #     raise OverflowError

        return m1_position_unsigned, m2_position_unsigned


if __name__ == "__main__":
    port = serial.Serial("COM4", baudrate=115200, timeout=0.1)
    time.sleep(2)
    claw = RoboClaw(port, 0x80)
    print(claw.get_temps())
    # claw.set_motor_positions(12000,
    #                          [6000, 1000],
    #                          [6000, 1000])
    # claw.set_motor_pwm(0, 0)

