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
        self.gpio_port = aConf.get_val_int("10_MOTOR_esc_gpio")
        self.gpio_power_port = aConf.get_val_int("11_MOTOR_power_gpio")
        self._gpio = pigpio.pi()
        GPIO.setup(self.gpio_power_port, GPIO.OUT)  # Active le controle du GPIO
        self._gpio.set_servo_pulsewidth(self.gpio_port, 0)
                
        # Initialisation du bouton asservissement moteur
        self.MOTOR_BUTTON_GPIO = aConf.get_val_int("12_MOTOR_button_gpio")
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.MOTOR_BUTTON_GPIO, GPIO.IN)              
        
        # Evénement pour commander l'arrêt du Thread
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 
                  
        # Paramètres Moteur
        self.tps_POSE=aConf.get_val_int("15_MOTOR_pause_time")
        self.vitesse_moteur=aConf.get_val_int("14_MOTOR_vitesse_favorite")
        self.vitesse_min = aConf.get_val_int("13_MOTOR_vitesse_min")
        
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
        
    def autoArm(self): 
        self.power_on()
        time.sleep(1)
        
        self.set_speed(self.vitesse_min)
        time.sleep(2)
        
        self.set_speed(self.vitesse_moteur)
        GPIO.wait_for_edge(self.MOTOR_BUTTON_GPIO,GPIO.RISING,timeout=5000)
        logging.info('Bouton asservissement Moteur détecté')
        time.sleep(2)
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
                GPIO.wait_for_edge(self.MOTOR_BUTTON_GPIO,GPIO.RISING,timeout=8000)
                logging.info('Bouton asservissement Moteur détecté')
                time.sleep(2)
                self.set_speed(0)
                
                # Temps de pose pour un secteur de 60°
                time_debut=time.time()
                delta_time=0
                while not self._pause_event.isSet() and delta_time < self.tps_POSE:
                    delta_time = time.time()-time_debut
                    time.sleep(0.5)
                    print(delta_time)
                    
            else: 
                self._continue_event.wait()  
        # End While        
        self.arret_complet() # arrêt relai
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
           
