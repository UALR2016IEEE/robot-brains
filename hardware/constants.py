class DataTypes(object):
    @staticmethod
    def member_of(data):
        return data in DataTypes.__dict__.values()


class Modes(object):
    @staticmethod
    def get_mode(value):
        return Modes.__dict__[value]

    @staticmethod
    def member_of(data):
        return data in Modes.__dict__.values()

    Single = 0x00
    Multiple = 0x01


class Commands(object):
    @staticmethod
    def get_command(value):
        return Commands.__dict__[value]

    Start_Scan = 0x20
    Force_Scan = 0x21
    Health = 0x52
    Stop_Scan = 0x25
    Reset = 0x40
    Info = 0x50


Start_Flag = 0xA5
