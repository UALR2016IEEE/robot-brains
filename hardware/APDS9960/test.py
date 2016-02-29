from .APDS9960 import APDS9960

sen = APDS9960()

sen.initialize()
sen.enableProximitySensor(None)
while True:
    print(sen.readRedLight(), sen.readBLueLight(), sen.readGreenLight())

