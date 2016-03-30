import atexit
import warnings
import time
from status_platform.status import StatusClass
import struct
from hardware.robo_claw import constants


class CommandNotReceived(Exception):
    pass


class ChecksumError(Exception):
    pass


class RoboClaw:
    REGISTER_ROBOCLAWS = {}
    def __init__(self, serial_port: StatusClass, address):
        self.REGISTER_ROBOCLAWS[(serial_port, address)] = self
        self.port = serial_port
        self._crc = 0
        self.address = address
        self.set_relitive_position()

    @atexit.register
    def cleanup():
        for (port, address), claw in RoboClaw.REGISTER_ROBOCLAWS.items():
            try:
                claw.set_motor_pwm(0, 0)
            except Exception as e:
                warnings.warn("RoboClaw @{}:{} failed to properly shutdown because:\n{}".format(port.port, hex(address), str(e)))

    def write(self, data):
        sent_data = struct.pack(">B{}s".format(len(data)), self.address, data)
        self.port.write(sent_data)
        return sent_data

    def read(self, length):
        return self.port.read(length)

    def set_relitive_position(self):
        self.rel_pos = self.get_raw_motor_positions()

    def send_command(self, command):
        with self.port.UART_mux():
            sent_data = self.write(command)
            crc = self.checksum(sent_data)
            self.port.write(struct.pack(">H", crc))

        raw_return_code = self.read(1)
        return_code, = struct.unpack(">B", raw_return_code)
        if return_code != 0xFF:
            raise CommandNotReceived()

    def ask(self, command, length):
        with self.port.UART_mux():
            sent_data = self.write(struct.pack(">B", command))
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
        self.set_relitive_position()
        m1_rel_pos, m2_rel_pos = self.rel_pos
        m1 = accel, m1[0], accel, m1[1] + m1_rel_pos
        m2 = accel, m2[0], accel, m2[1] + m2_rel_pos
        raw_data = struct.pack(
            ">BIIIiIIIi?",
            constants.MIXEDSPEEDACCELDECCELPOS,
            *m1,
            *m2,
            not buffered
        )
        try:
            self.send_command(raw_data)
        except struct.error:
            raise CommandNotReceived(
                "Sent position command with:\n\tm1_params:{}\n\tm2_params:{}\nCommand not recieved".format(m1, m2)
            )

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
        return (x - y for x, y in zip(self.get_raw_motor_positions(), self.rel_pos))

    def get_raw_motor_positions(self):
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

