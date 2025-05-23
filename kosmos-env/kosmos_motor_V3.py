#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Controle du moteur ESC

"""

import logging
from gpiozero import Button, DigitalOutputDevice, PWMOutputDevice
import time
from threading import Thread
from threading import Event

from kosmos_config import *

class kosmosEscMotor(Thread):

    def __init__(self, aConf: KosmosConfig):
        Thread.__init__(self)
        
        # Initialisation port GPIO ESC & RElai               
        self.Relai_GPIO = DigitalOutputDevice(aConf.config.getint(DEBUG_SECTION,"11_MOTOR_power_gpio"))
        self.PWM_GPIO = PWMOutputDevice(pin=aConf.config.getint(DEBUG_SECTION,"10_MOTOR_esc_gpio"),frequency=50)
        
        # Initialisation du bouton asservissement moteur
        self.Button_motor = Button(aConf.config.getint(DEBUG_SECTION,"12_MOTOR_button_gpio"))#,bounce_time=0.5)
        
        # Evénement pour commander l'arrêt du Thread
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 
                  
        # Paramètres Moteur
        self._Conf = aConf 
        self.tps_POSE=aConf.config.getint(CONFIG_SECTION,"15_MOTOR_pause_time")
        self.vitesse_moteur=aConf.config.getint(CONFIG_SECTION,"14_MOTOR_vitesse_favorite")
        self.vitesse_min = aConf.config.getint(CONFIG_SECTION,"13_MOTOR_vitesse_min")
        self.inertie_time = aConf.config.getint(CONFIG_SECTION,"16_MOTOR_inertie_time") # en ms
        self.timeout = aConf.config.getint(CONFIG_SECTION,"17_MOTOR_timeout") # en s
        self.pressORrelease = aConf.config.getint(CONFIG_SECTION,"18_MOTOR_pressORrelease")
        self.shift_time = aConf.config.getint(CONFIG_SECTION,"19_MOTOR_shift_time") # en ms

    def power_on(self):
        """Commande le relai d'alimentation de l'ESC"""
        self.Relai_GPIO.on() # Fermeture du relai

    def power_off(self):
        """Commande le relai d'alimentation de l'ESC"""
        self.Relai_GPIO.off() # Ouverture du relai
        self.Relai_GPIO.close()
        self.PWM_GPIO.close()
        self.Button_motor.close()
        
    def set_speed(self, aSpeed):
        """Lancement à la vitesse passée en paramètre
        1000 < vitesse < 2100 """
        self.PWM_GPIO.value=aSpeed*0.00005
        logging.debug(f"Moteur vitesse {aSpeed}.")    
        
    def autoArm(self): 
        self.power_on()
        time.sleep(1)
        
        self.set_speed(self.vitesse_min) # ne fait pas tourner le KOSMOS
        time.sleep(2)
        
        self.set_speed(self.vitesse_moteur) 
        time.sleep(self.shift_time/1000)
        if self.pressORrelease == 0:
            """
            if self.Button_motor.value == 1:
                time.sleep(self.shift_time/1000)
            else:
                time.sleep(0)
            """
            self.Button_motor.wait_for_press(timeout=self.timeout)
        if self.pressORrelease == 1:
            """
            if self.Button_motor.value == 0:
                time.sleep(self.shift_time/1000)
            else:
                time.sleep(0)
            """
            self.Button_motor.wait_for_release(timeout=self.timeout)
        logging.info('Bouton asservissement Moteur détecté')
        time.sleep(self.inertie_time/1000)
        self.set_speed(0)
        
        logging.info('Moteur et ESC prêts !')
        
    def arret_complet(self):
        self.set_speed(0)
        self.PWM_GPIO.off()
    
    def run(self):
        logging.info('Debut du thread moteur ESC.')
        while not self._t_stop:
            if not self._pause_event.isSet():
                
                event_line = self._Conf.get_date_HMS()  + ";START MOTEUR; " 
                self._Conf.add_line(EVENT_FILE,event_line)
                self.set_speed(self.vitesse_moteur)
                time.sleep(self.shift_time/1000)
                if self.pressORrelease == 0:
                    """
                    if self.Button_motor.value == 1:
                        time.sleep(self.shift_time/1000)
                    else:
                        time.sleep(0)
                    """
                    self.Button_motor.wait_for_press(timeout=self.timeout)
                if self.pressORrelease == 1:
                    """
                    if self.Button_motor.value == 0:
                        time.sleep(self.shift_time/1000)
                    else:
                        time.sleep(0)
                    """
                    self.Button_motor.wait_for_release(timeout=self.timeout)                    
                logging.info('Bouton asservissement Moteur détecté')
                time.sleep(self.inertie_time/1000)
                self.set_speed(0)
                
                event_line =  self._Conf.get_date_HMS()  + ";END MOTEUR; " 
                self._Conf.add_line(EVENT_FILE,event_line)
                
                time_debut=time.time()
                delta_time=0
                while not self._pause_event.isSet() and delta_time < self.tps_POSE:
                    delta_time = time.time()-time_debut
                    time.sleep(0.5)
                
            else:
                self._continue_event.wait()  
        # End While        
        self.arret_complet() #stop relai
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
           
