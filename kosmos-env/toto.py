import ms5837

pressure_sensor = ms5837.MS5837_30BA()

if pressure_sensor.init():
            
    print("Capteur de pression OK")
    
if pressure_sensor.read():
    print(pressure_sensor.pressure())