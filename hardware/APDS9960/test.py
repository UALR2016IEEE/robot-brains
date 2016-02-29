from .APDS9960 import APDS9960

sen = APDS9960()

sen.initialize()
while True:
    sen.enable_