#!/usr/bitn/env python3 -- coding: utf-8 --
""" Programme principal du KOSMOS en mode rotation Utilse une machine d'états D Hanon 12 décembre 2020 """
import logging
import time
from threading import Event
import threading
from gpiozero import LED, Button
import os

#Le programme est divisé en deux threads donc on a besoind du bibliotheque Thread
from threading import Thread

#Tous les methodes de l'API sont dans le fichier kosmos_backend.py
import kosmos_backend5 as KBackend

#Isolation du class KState dans le fichier kosmos_state.py
from kosmos_state import KState

from kosmos_config import *
import kosmos_config as KConf
import kosmos_csv as KCsv
import kosmos_cam5 as KCam
import kosmos_esc_motor5 as KMotor
import sys

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s : %(message)s',
                    datefmt='%d/%m %I:%M:%S')#,filename='kosmos.log')

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
        self._ledB = LED(self._conf.get_val_int("03_SYSTEM_led_b"))
        self._ledR = LED(self._conf.get_val_int("04_SYSTEM_led_r"))
        self._ledB.on()
        self._ledR.off()        

        # Boutons
        self.Button_Stop = Button(self._conf.get_val_int("02_SYSTEM_stop_button_gpio"))
        self.Button_Record = Button(self._conf.get_val_int("01_SYSTEM_record_button_gpio"))
        
        # Mode du système
        self.MODE=self._conf.get_val_int("00_SYSTEM_mode") 
        
        # Temps total de fonctionnement de l'appareil (pour éviter des crashs batteries)
        self.tps_total_acquisition = self._conf.get_val_int("07_SYSTEM_tps_fonctionnement") 
        
        #Paramètres camera & définition Thread Camera
        self.thread_camera = KCam.KosmosCam(self._conf)
        
        #Definition Thread CSV
        self.thread_csv = KCsv.kosmosCSV(self._conf)
        
        #Definition Thread Moteur
        self.PRESENCE_MOTEUR = self._conf.get_val_int("06_SYSTEM_moteur") # Fonctionnement moteur si 1
        if self.PRESENCE_MOTEUR==1:
            self.motorThread = KMotor.kosmosEscMotor(self._conf)
          
    def clear_events(self):
        """Mise à 0 des evenements attachés aux boutons"""
        self.record_event.clear()
        self.button_event.clear()
        self.stop_event.clear()

    def starting(self):
        logging.info("STARTING : Kosmos en train de démarrer")
        
        self._ledB.blink()
        
        self.thread_camera.initialisation_awb()
        
        if self.PRESENCE_MOTEUR == 1:
            self.motorThread.autoArm()       
        
        self.state = KState.STANDBY
    
    def standby(self):
        logging.info("STAND BY : Kosmos prêt")
        self._extinction = False 
        self._ledR.off()
        self._ledB.on()
        
        self.button_event.wait()
        if myMain.stop_event.is_set():
            self.state = KState.SHUTDOWN
        elif myMain.record_event.is_set():
            self.state = KState.WORKING
        #else:
        #    print('WTF !?')
              
    def working(self):
        logging.info("WORKING : Debut de l'enregistrement")       
        
        self._ledB.off()
                
        if self.PRESENCE_MOTEUR == 1:
            # Run thread moteur
            self.motorThread.restart()
        
        # Run thread CSV TP et GPS
        self.thread_csv.restart()
        
        # Run thread camera
        self.thread_camera.restart()
        
        # Attente d'un Event ou que le temps total soit dépassé
        while True:
            self.clear_events()
            self.record_event.wait(timeout = self.tps_total_acquisition)
            if myMain.record_event.is_set():
                logging.info('Sortie par bouton')
                break
            else:
                self._extinction = True
                logging.info('Sortie par extinction')
                break
                
        self.state = KState.STOPPING       
    
    def stopping(self):
        logging.info("STOPPING : Kosmos termine son enregistrement")
        
        self._ledB.off()
        self._ledR.blink()
        
        # Demander la fin de l'enregistrement
        self.thread_camera.stopCam()
        
        if self.PRESENCE_MOTEUR==1:
            # Pause Moteur
            self.motorThread.pause()
                
        # Pause Thread CSV TP 
        self.thread_csv.pause()
        
        if self._extinction == False:
            # On s'est arrêté via un bouton, on retourne donc en stand by
            self.state = KState.STANDBY
        elif self._extinction == True:
            # On s'est arrêté car arrivé au bout du temps_total de fonctionnement du système
            time.sleep(5) #tempo pour gérer la boucle while d'enregistrement
            self.state = KState.SHUTDOWN
        
    def shutdown(self):
        logging.info("SHUTDOWN : Kosmos passe à l'arrêt total")
              
        self._ledR.on()
        
        # Arrêt de l'écriture du CSV TP
        self.thread_csv.stop_thread()
        if self.thread_csv.is_alive():
            self.thread_csv.join()
    
        # Arrêt de la caméra
        self.thread_camera.closeCam()   # Stop caméra
        if self.thread_camera.is_alive():
            self.thread_camera.join()   # Caméra stoppée
        
        # Arrêt du moteur
        if self.PRESENCE_MOTEUR==1:  
            self.motorThread.stop_thread() 
            if self.motorThread.is_alive(): 
                self.motorThread.join() 
            self.motorThread.power_off()
        
        # Extinction des LEDs
        self._ledR.off()
        self._ledB.off()
        
        #Arrêt du logging
        logging.shutdown()

        # Commande de stop au choix arrêt du programme ou du PC
        if self._conf.get_val_int("05_SYSTEM_shutdown") != 0 :
            os.system("sudo shutdown -h now")
        else :
            sys.exit(0)

    def modeRotatif(self):
        """programme principal du mode rotatif"""
        while True:
            if self.state == KState.STARTING:
                self.starting()
                time.sleep(0.5)
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
    if not myMain.stop_event.is_set():
        logging.debug("Bouton shutdown pressé")
        myMain.stop_event.set() 
        myMain.button_event.set() # cette ligne permet d'activer le button global

def record_cb(channel):
    """Callback du bp start/stop record"""
    if not myMain.record_event.is_set():
        logging.debug("Bouton start/stop pressé")
        myMain.record_event.set()
        myMain.button_event.set() # cette ligne permet d'activer le button global

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
    #GPIO.add_event_detect(myMain.STOP_BUTTON_GPIO, GPIO.FALLING, callback=stop_cb, bouncetime=500)
    #GPIO.add_event_detect(myMain.RECORD_BUTTON_GPIO, GPIO.FALLING, callback=record_cb, bouncetime=500)
    
    myMain.Button_Stop.when_held = stop_cb
    myMain.Button_Record.when_held = record_cb
    

    # Debut prog principal :
    myMain.modeRotatif()

#Creation des deux threads t1 et t2
t1=Thread(target=main,args=[])
t2=Thread(target=flaskMain,args=[])

#Lancement des deux threads
t1.start()
t2.start()
