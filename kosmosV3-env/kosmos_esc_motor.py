#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Controle du moteur ESC
Utilise la lib pigpio

- Modif du 20 janvier pour remettre la calibration.
- Modif du 1 février : changement de la méthode d'armement.
- Modif du 26 février 2021 : ajout du relai d'alimentation et utilisation pour calibrer et armer
"""
import logging
import RPi.GPIO as GPIO  # Importe la bibliotheque pour contrôler les GPIOs
import time
import pigpio  # importing GPIO library
from threading import Thread
from threading import Event
from kosmos_config import *
#import subprocess

#Paramètres moteurs demandés par KosmosConfig
"""
SETT_ESC_MOTOR_GPIO=22
SETT_POWER_MOTOR_GPIO=27
SETT_ESC_MOTOR_MAX_VAL=2100 # Inutile
SETT_ESC_MOTOR_MIN_VAL=1000
SETT_ESC_MOTOR_FAVORITE_VAL=1350
SETT_MOTOR_STOP_TIME=27 
SETT_MOTOR_RUN_TIME=5 # Inutile

SETT_MOTOR_BUTTON_GPIO = 21

"""
class kosmosEscMotor(Thread):

    def __init__(self, aConf: KosmosConfig):
        Thread.__init__(self)
        # os.system ("sudo pigpiod") #Launching GPIO library
        result = subprocess.run(["sudo", "pigpiod"], capture_output=True) 
        time.sleep(0)  # FIXME attendre que la lib soit chargée ?
        # vérif avec sudo killall pigpiod
        if result.returncode == 0:
            logging.debug(f"Moteur : libairie pigpiod chargée.")
        else:
            logging.error(f"Problème avec libairie pigpiod {result.stdout.decode()}")

        # Initialisation port GPIO ESC & RElai
        self.gpio_port = aConf.get_val_int("SETT_ESC_MOTOR_GPIO")
        self.gpio_power_port = aConf.get_val_int("SETT_POWER_MOTOR_GPIO")
        self._gpio = pigpio.pi()
        GPIO.setup(self.gpio_power_port, GPIO.OUT)  # Active le controle du GPIO
        self._gpio.set_servo_pulsewidth(self.gpio_port, 0)
                
        # Initialisation du bouton asservissement moteur
        #self.motor_event = Event()  # l'ILS du moteur activé
        self.MOTOR_BUTTON_GPIO = aConf.get_val_int("SETT_MOTOR_BUTTON_GPIO")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MOTOR_BUTTON_GPIO, GPIO.IN)              
        
        # Evénement pour commander l'arrêt du Thread
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 
                  
        # Paramètres Moteur
        self.tps_POSE=aConf.get_val_int("SETT_MOTOR_STOP_TIME")
        self.vitesse_moteur=aConf.get_val_int("SETT_ESC_MOTOR_FAVORITE_VAL")
        self.vitesse_min = aConf.get_val_int("SETT_ESC_MOTOR_MIN_VAL")
        
    def power_on(self):
        """Commande le relai d'alimentation de l'ESC"""
        GPIO.output(self.gpio_power_port, GPIO.HIGH) # Coupure du relai

    def power_off(self):
        """Commande le relai d'alimentation de l'ESC"""
        GPIO.output(self.gpio_power_port, GPIO.LOW) # Coupure du relai
        
    def set_speed(self, aSpeed):
        """Lancement à la vitesse passée en paramètre
        1000 < vitesse < 2100 """
        self._gpio.set_servo_pulsewidth(self.gpio_port, aSpeed)
        logging.debug(f"Moteur vitesse {aSpeed}.")    
        
    def moove(self, aSpeed, aTime):
        """Lancement à la vitesse et temps passés en paramètre
        0 < vitesse < 2100 """
        self.set_speed(aSpeed)
        time.sleep(aTime)
        
    def autoArm(self): 
        self.power_on()
        time.sleep(1)
        self.moove(self.vitesse_min, 2) 
        self.set_speed(self.vitesse_moteur)
        GPIO.wait_for_edge(self.MOTOR_BUTTON_GPIO,GPIO.RISING)
        self.set_speed(0)
        logging.info('Moteur et ESC prêts !')
        
    def arret_complet(self):
        #This will stop every action your Pi is performing for ESC ofcourse.
        self.set_speed(0)
        self._gpio.stop()
    
    def run(self):
        logging.info('Debut du thread moteur ESC.')
        while not self._t_stop:
            if not self._pause_event.isSet():
                self.set_speed(self.vitesse_moteur)
                GPIO.wait_for_edge(self.MOTOR_BUTTON_GPIO,GPIO.RISING)
                logging.info('Bouton asservissement Moteur détecté')
                self.set_speed(0)
                time.sleep(self.tps_POSE)
            else:
                self.set_speed(0)
                self._continue_event.wait()  
        # End While        
        self.arret_complet()
   
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
           
