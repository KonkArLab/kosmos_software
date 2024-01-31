#!/usr/bin/env python3 -- coding: utf-8 --
""" Programme principal du KOSMOS en mode rotation Utilse une machine d'états D Hanon 12 décembre 2020 """
import logging
import time
from threading import Event
import RPi.GPIO as GPIO
import os

#Le programme est divisé en deux threads donc on a besoind du bibliotheque Thread
from threading import Thread

#Tous les methodes de l'API sont dans le fichier kosmos_backend.py
import kosmos_backend as KBackend

#Isolation du class KState dans le fichier kosmos_state.py
from kosmos_state import KState

import kosmos_config as KConf
import kosmos_csv as KCsv
import kosmos_led as KLed
import kosmos_cam as KCam
import kosmos_esc_motor as KMotor
import sys

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s : %(message)s',
                    datefmt='%d/%m %I:%M:%S',
                    filename='kosmos.log')

class kosmos_main():

    """ 
        On a divisé l'initialisation en deux methodes:
        Dans le constructeur, on a conservé la creation des evenement qui doit s'executé seulement une fois dans tous le programme.
        Une methode init() qui contient le reste d'initialisation qui peut étre appeler plusieur fois au besoin.
    """
    def __init__(self):
         # évènements
        self.button_event = Event()  # un ILS a été activé
        self.record_event = Event()  # l'ILS start or stop record été activé
        self.stop_event = Event()    # l'ILS du shutdown or stop record activé
        self.init()

    def init(self):
        # Lecture du fichier de configuration
        self._conf = KConf.KosmosConfig()
        self.state = KState.STARTING

        # LEDs
        self._ledB = KLed.kosmos_led(self._conf.get_val_int("SETT_LED_B"))
        self._ledR = KLed.kosmos_led(self._conf.get_val_int("SETT_LED_R"))
        self._ledB.start()
        self._ledR.set_off()

        # Boutons
        self.STOP_BUTTON_GPIO = self._conf.get_val_int("SETT_STOP_BUTTON_GPIO")
        self.RECORD_BUTTON_GPIO = self._conf.get_val_int("SETT_RECORD_BUTTON_GPIO")
        GPIO.setmode(GPIO.BCM)  # on utilise les n° de GPIO et pas les broches
        GPIO.setup(self.STOP_BUTTON_GPIO, GPIO.IN)
        GPIO.setup(self.RECORD_BUTTON_GPIO, GPIO.IN)
        
        #Mode 1 pour staviro
        self.MODE=self._conf.get_val_int("SETT_MODE") # à mettre dans le ini
        
        #Paramètres camera
        self.tps_record=self._conf.get_val_int("SETT_RECORD_TIME")
        self.thread_camera = KCam.KosmosCam(self._conf)
        
        

    def clear_events(self):
        """Mise à 0 des evenements attachés aux boutons"""
        self.record_event.clear()
        self.button_event.clear()
        self.stop_event.clear()

    def starting(self):
        """Le kosmos est en train de démarrer"""
        logging.info("ETAT : Kosmos en train de démarrer")
        time.sleep(1) # temporise pour éviter de trop tirer d'ampère et de faire sauter le relai (si utilisation d'une alim labo, s'assurer qu'elle délivre au moins 2A  à 12.5 V)
        self.thread_csv = KCsv.kosmosCSV(self._conf)
        self.thread_csv.start()
        self._ledB.pause()
        if (self.MODE == 1) :
            self.state = KState.STANDBY
        else :
            self.state = KState.WORKING

    def standby(self):
        """Le kosmos est en attente du lancement de l'enregistrement"""
        logging.info("ETAT : Kosmos prêt")
        self._ledB.set_on()
        self.button_event.wait()
        if myMain.stop_event.isSet():
            self.state = KState.SHUTDOWN
        else:
            if myMain.record_event.isSet():
                self.state = KState.WORKING
        self._ledB.set_off()
      
    def working(self):
        logging.info("ETAT : Kosmos en enregistrement")
        self._ledB.set_off()
        self.thread_camera.restart()
        while True :
            self.clear_events()
            if myMain.record_event.isSet():
                print('break')
                break
            else:
                continue                   
        self.state =KState.STOPPING       
    
    def stopping(self):
        logging.info("ETAT : Kosmos termine son enregistrement")
        self._ledR.startAgain()
        # Demander la fin de l'enregistrement
        self.thread_camera.stopCam()
        logging.info("thread caméra terminé")
        self._ledR.pause()
        if (self.MODE == 1 ):
            # prochain état : stopping
            self.state = KState.STANDBY
        else:
            self.state = KState.SHUTDOWN

    def shutdown(self):
        logging.info("ETAT : Kosmos passe à l'arrêt total")

        self.thread_camera.closeCam()   # Stop caméra

        self.thread_csv.stop_thread()  # Arrêt de l'écriture du CVS
        self.thread_csv.join()
        logging.info("Thread csv terminé.")

        if self.thread_camera.is_alive():
            self.thread_camera.join()   # Caméra stoppée

        if self._ledB.is_alive():
            self._ledB.stop()
            self._ledB.join()
            self._ledB.set_off()    # Led bleue stoppée
        if self._ledR.is_alive():
            self._ledR.stop()
            self._ledR.join()   # Led rouge stoppée
        self._ledR.set_on()
        logging.shutdown()

        # Commande de stop au choix arrêt du programme ou du PC
        if self._conf.get_val_int("SETT_SHUTDOWN") != 0 :
            os.system("sudo shutdown -h now")
        else :
            sys.exit(0)

    def modeRotatif(self):
        """programme principal du mode rotatif"""
        while True:
            print("recherche sate",self.state)          
            if self.state == KState.STARTING:
                self.starting()
                time.sleep(1)
                self.clear_events()

            if self.state == KState.STANDBY:
                self.standby()
                time.sleep(0.5)
                self.clear_events()

            if self.state == KState.WORKING:
                self.working()
                time.sleep(0.5)
                self.clear_events()

            if self.state == KState.STOPPING:
                self.stopping()
                time.sleep(0.5)
                self.clear_events()

            if self.state == KState.SHUTDOWN:
                self.shutdown()

# Fin de la classe kosmos_main

def stop_cb(channel):
    """Callback du bp shutdown"""
    if not myMain.stop_event.isSet():
        logging.debug("bp shutdown pressé")
        myMain.stop_event.set()
        myMain.button_event.set()

def record_cb(channel):
    """Callback du bp start/stop record"""
    if not myMain.record_event.isSet():
        logging.debug("bp start/stop record pressé")
        myMain.record_event.set()
        myMain.button_event.set()

#Instance du classe principale
myMain = kosmos_main()

#Instance du classe Server
server = KBackend.Server(myMain)

#Le targuet du Thread t2 qui est le thread du backend.
def flaskMain():
    server.run()
    
#Le targuet du Thread t1 qui est le thread du programme principale.
def main():
    # Liens entre les boutons et les fonction de callback
    GPIO.add_event_detect(myMain.STOP_BUTTON_GPIO, GPIO.FALLING, callback=stop_cb, bouncetime=500)
    GPIO.add_event_detect(myMain.RECORD_BUTTON_GPIO, GPIO.FALLING, callback=record_cb, bouncetime=500)

    # Debut prog principal :
    myMain.modeRotatif()

#Creation des deux threads t1 et t2
t1=Thread(target=main,args=[])
t2=Thread(target=flaskMain,args=[])

#Lancement des deux threads
t1.start()
t2.start()
