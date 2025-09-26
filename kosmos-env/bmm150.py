# fichier ini_magneto.py
import sys
import time
#sys.path.append("/home/kosmos/Documents/Scripts_magneto_lumiere")
from DFRobot_bmm150 import *

class magnetoSensor:
    def __init__(self, bus=1, address=0x13):  # Adresse par défaut : 0x13
        self.sensor = DFRobot_bmm150_I2C(bus, address)
        gX = None
        gY = None
        gZ = None

    def init(self):
        try:
            while self.sensor.ERROR == self.sensor.sensor_init():
                time.sleep(1)
            self.sensor.set_operation_mode(self.sensor.POWERMODE_NORMAL)
            self.sensor.set_preset_mode(self.sensor.PRESETMODE_HIGHACCURACY)
            self.sensor.set_rate(self.sensor.RATE_10HZ)
            self.sensor.set_measurement_xyz()
            return True
        except:
            return False

    def read(self):
        try:
            geomagnetic = self.sensor.get_geomagnetic()  # renvoie (x, y, z)
            gX = geomagnetic[0]
            gY = geomagnetic[1]
            gZ = geomagnetic[2]
            compass = self.sensor.get_compass_degree()
            return gX, gY, gZ, compass
        except:
            return
