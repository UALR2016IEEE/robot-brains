import json


class Conversion:
    def __init__(self):

        self.config = {}

        with open('/home/pi/2016/robot-brains-old/config.json', 'r') as f:
            self.config = json.load(f)
    
        conversion_factor = self.config["map characteristics"]["map size meters"] * 1000.0 / self.config["map characteristics"]["map size pixels"]
    
        self.config["mm2pix"] = 1.0 / conversion_factor
        self.config["pix2mm"] = conversion_factor

    def mm2pix(self, mm):
        return int(mm * self.config["mm2pix"])

    def pix2mm(self, pix):
        return int(pix * self.config["pix2mm"])
