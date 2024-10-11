#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Controle du moteur via communication i2c avec Arduino Nano
Le code ci-dessous envoie une liste de paramètres à l'Arduino qui permet de modifier le comportement de la rotation moteur
Le code fonctionne mais est encore en chantier, pas mal de choses restent à optimiser
"""
import logging
from gpiozero import Button, DigitalOutputDevice, PWMOutputDevice
from threading import Thread
from threading import Event
import time
from kosmos_config import *

try:
    import smbus
except:
    print ('Try sudo apt install python3-smbus2') #D. Hanon ajout de () pour être compatible python_3


class kosmosMotor(Thread):

    def __init__(self, aConf: KosmosConfig):
        
        Thread.__init__(self)

        try:
            self._bus = smbus.SMBus(1)
        except:
            print("Bus %d is not available.") % bus
            print("Available busses are listed as /dev/i2c*")
            self._bus = None
        
        # Evénement pour commander l'arrêt du Thread
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 

        self.wakeUp_GPIO = DigitalOutputDevice(aConf.config.getint(CONFIG_SECTION, "09_SYSTEM_wake_up_motor"))
        self.wakeUp_GPIO.off()
      
        self._address = 0x04
        self._state = 1
        self._sleep_mode = 0
        
        # Paramètres Moteur
        self.motor_revolutions = aConf.config.getint(CONFIG_SECTION, "10_MOTOR_revolutions")
        # 10 revolutions : 60°
        self.motor_vitesse = aConf.config.getint(CONFIG_SECTION, "11_MOTOR_vitesse")
        # minimum : 1 ; maximum : 250
        self.motor_accel = aConf.config.getint(CONFIG_SECTION, "12_MOTOR_acceleration")
        # minimum : 1 ; maximum : 250
        self.pause_time = aConf.config.getint(CONFIG_SECTION, "13_MOTOR_pause_time")
        # en s
        self.step_mode = aConf.config.getint(CONFIG_SECTION, "14_MOTOR_step_mode")
        # 1 pour full_step, 2 pour 1/2 microstep, 4 pour 1/4 microstep, 16 pour 1/16 microstep etc
        self.i2c_period = aConf.config.getint(CONFIG_SECTION, "15_MOTOR_i2c_communication_period")
        # en s

    def power_on(self):
        # déclencher une interruption pour réveiller l'arduino si elle est en mode deep sleep
        self.wakeUp_GPIO.on()
        time.sleep(1)
        self.wakeUp_GPIO.off()
      
    def power_off(self):
        """Commande l'arrêt de la rotation moteur (fonction appelée par la main en cas de shutdown)"""
        self.wakeUp_GPIO.off()
        self._state = 0
        self._sleep_mode = 1
        self.send_data()
        self._bus.close()

    def send_data(self):
        i2c_Data = [self._state + 1, self.motor_revolutions, self.motor_vitesse, self.motor_accel, self._sleep_mode + 1, self.step_mode]
        # self.step_mode paramètre à enlever de la transmission à l'avenir
        try:
                self._bus.write_i2c_block_data(self._address, 0x00, i2c_Data)
        except:
                logging.error('Erreur moteur : transmission Arduino i2c impossible')

    def autoArm(self): 
        '''activation de la rotation moteur 1 fois pour témoigner de son fonctionnement à l'allumage'''
        self.power_on()
        self.send_data()
        
        logging.info('Moteur prêt !')
    
    def run(self):
        logging.info('Debut du thread moteur.')
        while not self._t_stop:
            if not self._pause_event.isSet():
                while not self._pause_event.isSet():
                
                    self._state = True
                    self.send_data()
                    rotation_done = False
                    
                    while not self._pause_event.isSet() and not rotation_done :
                            try :
                                rotation_done = self._bus.read_byte(self._address)
                            except :
                                logging.error('Erreur moteur : réception Arduino impossible')
                            time.sleep(0.5)
                            
                    time_debut=time.time()
                    delta_time=0
                    while not self._pause_event.isSet() and delta_time < self.pause_time:
                            delta_time = time.time()-time_debut
                            time.sleep(0.1)
            else:
                self._state = 0
                self.send_data()
                self._continue_event.wait()  
        # End While        
        logging.info("Thread moteur terminé")
   
    def stop_thread(self):
        """positionne l'évènement qui va provoquer l'arrêt du thread"""
        self._t_stop = True
        self._continue_event.set()
        self._pause_event.set()
  
    def pause(self):
        """suspend le thread pour pouvoir le redémarrer."""
        self._continue_event.clear()
        self._pause_event.set()

    def restart(self):
        """Relance le thread"""
        if self.is_alive():
            self._pause_event.clear()
            self._continue_event.set()
        else:
            self.start()
