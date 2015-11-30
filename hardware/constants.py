__author__ = 'StaticVOiDance'

class DataTypes:
    @staticmethod
    def member_of(data):
        return data in DataTypes.__dict__.values()

class Modes:
    @staticmethod
    def get_mode(value):
        return Modes.__dict__[value]

    @staticmethod
    def member_of(data):
        return data in Modes.__dict__.values()

    Single = 0x00
    Multiple = 0x01

class Commands:
    @staticmethod
    def get_command(value):
        return Commands.__dict__[value]

    Start_Scan = b"\x20"
    Force_Scan = b"\x21"
    Health = b"\x51"
    Stop_Scan = b"\x25"
    Reset = b"\x40"
    Info = b"0x50"


Start_Flag = 0xA5