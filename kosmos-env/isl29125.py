# fichier rgb_sensor_module.py
import smbus
import time
import logging

class RGBSensor:
    def __init__(self, bus_id=1):
        self.bus = smbus.SMBus(bus_id)
        self.address = 0x44
        red = None
        blue = None
        green = None

    def init(self):
        try:
            self.bus.write_byte_data(self.address, 0x01, 0x0D)  # RGB, 10000 lux, 16 bits
            time.sleep(0.5)
            return True
        except Exception :
            return False

    def read(self):
        try:
            data = self.bus.read_i2c_block_data(self.address, 0x09, 6)
            green = data[1] << 8 | data[0]
            red   = data[3] << 8 | data[2]
            blue  = data[5] << 8 | data[4]
            return red, green, blue
        except:
            return
            # return "", "", ""