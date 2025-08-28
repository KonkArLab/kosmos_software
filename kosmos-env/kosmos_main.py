#!/usr/bitn/env python3 -- coding: utf-8 --
""" Programme principal du KOSMOS en mode rotation Utilse une machine d'états D Hanon 12 décembre 2020 """
import logging
import time
from threading import Event
import threading
from gpiozero import LED, Button, TonalBuzzer,DigitalOutputDevice
import os
import json
import glob

#Le programme est divisé en deux threads donc on a besoind du bibliotheque Thread
from threading import Thread

#Tous les methodes de l'API sont dans le fichier kosmos_backend.py
import kosmos_backend as KBackend
from kosmos_melody import *

#Isolation du class KState dans le fichier kosmos_state.py
from kosmos_state import KState

from kosmos_config import *
import kosmos_config as KConf

# Import des classes caméra
import kosmos_cam as KCam
import magpi_cam as MCam

# Import des classes moteur pour les v 3 et 4
import kosmos_motor_V3 as KMotor3
import kosmos_motor_V4 as KMotor4

import sys
import ms5837
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
        self._ledB = LED(self._conf.config.getint(DEBUG_SECTION,"03_SYSTEM_led_b"))
        self._ledR = LED(self._conf.config.getint(DEBUG_SECTION,"04_SYSTEM_led_r"))
        self._ledB.on()
        self._ledR.off()        

        # Buzzer
        if self._conf.systemVersion == "4.0":
            self.BUZZER_ENABLED = self._conf.config.getint(CONFIG_SECTION, "09_BUZZER")
            if self.BUZZER_ENABLED == 1:
                self._buzzer = TonalBuzzer(self._conf.config.getint(DEBUG_SECTION, "08_SYSTEM_buzzer"), octaves = 3)
                logging.info("BUZZER demandé !")
            else:
                logging.info("BUZZER non demandé")    
        else:
            self.BUZZER_ENABLED = 0
            logging.info("BUZZER non demandé")    
        
        # Boutons
        self.Button_Stop = Button(self._conf.config.getint(DEBUG_SECTION,"02_SYSTEM_stop_button_gpio"))
        self.Button_Record = Button(self._conf.config.getint(DEBUG_SECTION,"01_SYSTEM_record_button_gpio"))
        
        # Mode du système   #1 STAVIRO     #2 MICADO
        self.MODE = self._conf.config.getint(CONFIG_SECTION,"00_STAVIRO_MICADO") 
        if self.MODE==1:
            logging.info("MODE STAVIRO demandé")    
        elif self.MODE==2: 
            logging.info("MODE MICADO demandé")
            # Chargement du temps de veille entre deux prises de vue
            self.tps_veille =  self._conf.config.getint(CONFIG_SECTION,"04_TPS_VEILLE")#temps de veille en seconde
        self.bool_micado = 1 # init du booléen micado

        

        # Temps total de fonctionnement de l'appareil (pour éviter des crashs batteries)
        self.tps_total_acquisition = self._conf.config.getint(CONFIG_SECTION,"03_TPS_FONCTIONNEMENT")         
        
        # Definition Thread Moteur
        self.PRESENCE_MOTEUR = self._conf.config.getint(CONFIG_SECTION,"05_MOTEUR") # Fonctionnement moteur si 1
        if self.PRESENCE_MOTEUR==1:
            if self._conf.systemVersion == "4.0":
                self.motorThread = KMotor4.kosmosMotor(self._conf)
            if self._conf.systemVersion == "3.0":
                self.motorThread = KMotor3.kosmosEscMotor(self._conf)
            else:
                logging.info("Moteur demandé mais non initialisé")
        
        # Instructions visiblement essentielles au bon fonctionnement du TP quand le moteur ne marche pas
        if self.PRESENCE_MOTEUR == 0 and self._conf.systemVersion == "4.0":
            self.wakeUp_GPIO = DigitalOutputDevice(self._conf.config.getint(DEBUG_SECTION, "09_SYSTEM_wake_up_motor"))
            self.wakeUp_GPIO.off()
                
        # Type d'enregistrement : TimeLapse ou Caméra
        self.ENREGISTREMENT = self._conf.config.getint(CONFIG_SECTION,"01_CAM_TIMELAPSE") 
        # Paramètres camera & définition Thread Camera
        if self.ENREGISTREMENT == 2:
            logging.info("ENREGISTREMENT de type time lapse") 
            self.thread_camera = MCam.MagpiCam(self._conf)
        else:
            logging.info("ENREGISTREMENT de type vidéo") 
            self.thread_camera = KCam.KosmosCam(self._conf)
    
        
    def clear_events(self):
        """Mise à 0 des evenements attachés aux boutons"""
        self.record_event.clear()
        self.button_event.clear()
        self.stop_event.clear()

    def starting(self):
        logging.info("STARTING : Kosmos en train de démarrer")
        
        self._ledB.blink()
        
        # Buzzer si version 4
        if self._conf.systemVersion == "4.0":
            if self.BUZZER_ENABLED == 1:
                playMelody(self._buzzer, STARTING_MELODY)
        
        self.thread_camera.initialisation_awb()
        
        if self.PRESENCE_MOTEUR == 1:
            self.motorThread.autoArm()       
        
        self.state = KState.STANDBY
    
    def standby(self):
        logging.info("STAND BY : Kosmos prêt")
        self._extinction = False 
        self._ledR.off()
        self._ledB.on()
        
        # Buzzer si version 4
        if self._conf.systemVersion == "4.0" :
            if self.BUZZER_ENABLED == 1:
                playMelody(self._buzzer, STANDBY_MELODY)
                time.sleep(0.1)

        # Gestion des modes MICADO/STAVIRO
        if self.MODE == 2 and self.bool_micado == 1: # Mode MICADO sans intervention de l'opérateur via bouton 'stop record' 
            self.state = KState.WORKING
        else: # Mode STAVIRO ou MODE MICADO avec arrêt via bouton 'stop record'      
            self.button_event.wait()
            if myMain.stop_event.is_set():
                self.state = KState.SHUTDOWN
            elif myMain.record_event.is_set():
                self.state = KState.WORKING
                 
    def working(self):
        logging.info("WORKING : Debut de l'enregistrement")
        
        if self.MODE == 2: # Mode MICADO
            #On remet le booléen à 1 pour que l'enregistrement suive la programmation automatique
            self.bool_micado = 1
        
        increment = self._conf.system.getint(INCREMENT_SECTION,"increment")        
        # Création du dossier enregistrement dans le dossier Campagne
        os.chdir(self._conf.CAMPAGNE_PATH)
        self.video_file = f'{increment:04}'
        if os.path.exists(self.video_file):
            pass
        else:
            os.mkdir(self.video_file)
        VID_PATH = self._conf.CAMPAGNE_PATH+self.video_file
        os.chdir(VID_PATH) # Ligne très importante pour bonne destination des fichiers !!!

        # Initialisation de fichier Event
        event_line = "Heure;Event;Fichier"        
        self._conf.add_line(EVENT_FILE,event_line)
      
        self._ledB.off()
        
        # Buzzer si version 4
        if self._conf.systemVersion == "4.0" :
            if self.BUZZER_ENABLED == 1:
                playMelody(self._buzzer, WORKING_MELODY)
        
        if self.PRESENCE_MOTEUR == 1:
            # Run thread moteur
            self.motorThread.restart()
        
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
        
        #increment du code station
        self._conf.system.set(INCREMENT_SECTION,"increment",str(increment+1))       
        self._conf.update_system()
        
        self.state = KState.STOPPING       
    
    def stopping(self):
        logging.info("STOPPING : Kosmos termine son enregistrement")
        
        self._ledB.off()
        self._ledR.blink()
        
        # Buzzer si version 4
        if self._conf.systemVersion == "4.0" :
            if self.BUZZER_ENABLED == 1:
                playMelody(self._buzzer, STOPPING_MELODY)
        
        # Demander la fin de l'enregistrement
        self.thread_camera.stopCam()
        
        if self.PRESENCE_MOTEUR==1:
            # Pause Moteur
            self.motorThread.pause()
        
        if self._extinction == False:
            # On s'est arrêté via un bouton, on retourne donc en stand by
            if self.MODE==2: #En mode MICADO, si on est passé par un arrêt via bouton, la vidéo ne doit pas se lancer
                self.bool_micado = 0
            self.state = KState.STANDBY
            event_line = self._conf.get_date_HMS()  + "; SORTIE BOUTON"
            self._conf.add_line(EVENT_FILE,event_line)
            
        elif self._extinction == True:
            event_line = self._conf.get_date_HMS()  + "; SORTIE DUREE LIMITE"
            self._conf.add_line(EVENT_FILE,event_line)
            # On s'est arrêté car arrivé au bout du temps_total de fonctionnement du système
            time.sleep(5) #tempo pour gérer la boucle while d'enregistrement
            self.state = KState.SHUTDOWN
        
    def arretThreads(self):
        logging.info("Arret des Threads pour Reboot ou Shutdown")
        self._ledR.on()
        self._ledB.off()
        
        self.Button_Stop.close() 
        self.Button_Record.close()
        
        # Buzzer si version 4
        if self._conf.systemVersion == "4.0" :
            if self.BUZZER_ENABLED == 1:
                playMelody(self._buzzer, SHUTDOWN_MELODY)
                self._buzzer.stop()
                self._buzzer.close()
    
        if self.PRESENCE_MOTEUR==1:
            self.motorThread.stop_thread()
            self.motorThread.power_off()       
            if self.motorThread.is_alive(): 
                self.motorThread.join()
            del self.motorThread
            
        if self.PRESENCE_MOTEUR == 0 and self._conf.systemVersion == "4.0":
                self.wakeUp_GPIO.off()
                self.wakeUp_GPIO.close()   
         
        # Arret Camera   
        if self.ENREGISTREMENT != 2:
            if self.thread_camera.PRESENCE_HYDRO==1:
                del self.thread_camera.thread_hydrophone
        self.thread_camera.closeCam()
        if self.thread_camera.is_alive():
            self.thread_camera.join()   # Caméra stoppée    
        del self.thread_camera
                
        self._ledR.off()
        self._ledR.close()
        self._ledB.close()
        
            
    def shutdown(self):
        logging.info("SHUTDOWN : Kosmos passe à l'arrêt total")
        
        # Arret des threads du systeme
        self.arretThreads()
   
        if self.MODE == 2 and self.bool_micado == 1: #Mode MICADO avec temps écoulé
            logging.info("MISE EN VEILLE PROFONDE")
            self.copyLog()
            logging.shutdown()
            os.system("echo +"+str(self.tps_veille)+" | sudo tee /sys/class/rtc/rtc0/wakealarm")
            os.system("sudo halt")
        else: # Mode STAVIRO ou Mode MICADO avec arrêt par bouton
            # Commande de stop au choix arrêt du programme ou du PC
            if self._conf.config.getint(CONFIG_SECTION,"06_SHUTDOWN") != 0 :
                logging.info("EXTINCTION DU KOSMOS")
                self.copyLog()
                logging.shutdown()
                os.system("sudo shutdown -h now")
            else :
                # Pas de copie du log si simple arret du soft. Car il est possible d'aller le voir directement sur la carte SD. 
                logging.info("ARRET DU SOFT KOSMOS")
                logging.shutdown()
                os._exit(0)

    def copyLog(self):
        # Copie du log dans le dossier Campagne
        try:
            logging.info("Copie du LOG")
            LAST_LOG = max(glob.iglob(LOG_PATH + "*.log"),key=os.path.getctime).split('/')[-1]
            subprocess.run(["sudo", "cp", "-n", LOG_PATH+LAST_LOG,self._conf.CAMPAGNE_PATH+LAST_LOG])
        except:
            logging.info("Erreur de copie du LOG")
    
    
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
