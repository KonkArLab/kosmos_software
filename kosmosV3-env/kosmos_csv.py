#!/usr/bin/python
# coding: utf-8
from datetime import datetime

from threading import Thread
from threading import Event

import logging
import os
import ms5837  # librairie du capteur de pression et temperature

from kosmos_config import *


class kosmosCSV(Thread):
    """Classe dérivée de Thread qui gère l'enregistrement du CSV"""

    def __init__(self, aConf: KosmosConfig):
        """Constructeur de la classe kosmosCSV
        Parameters :
            aConf : la classe qui lit le fichier de configuration

        Sont lus dans le fichier de configuration :
            - 20_CSV_step_time la période échtillonage
            - 21_CSV_file_name la base du nom du fichier CSV
        """
        
        Thread.__init__(self)
        
        # Evénement pour commander l'arrêt du Thread
        self._stopevent = Event()
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False
        
        self._time_step = aConf.get_val_int("20_CSV_step_time")
        self._file_name = aConf.get_val("21_CSV_file_name") + "_"
        
        os.chdir(USB_INSIDE_PATH)
        if not os.path.exists("CSV"): 
                os.mkdir("CSV")
        os.chdir(WORK_PATH)
        
        # Initialisation Capteur TP
        self._press_sensor_ok = False
        try:
            # capteur T et P Default I2C bus is 1 (Raspberry Pi 3)
            self.pressure_sensor = ms5837.MS5837_30BA()
            if self.pressure_sensor.init():
                self._press_sensor_ok = True
            logging.info("Capteur de pression OK")
        except:
            logging.error("Erreur d'initialisation du capteur de pression")
        self.stop = False

    def run(self):
        """Ecriture des données sur le fichier CSV"""
        while self.stop is False:
            logging.info("Fichier CSV ouvert")
            dateN = datetime.now()
            print(os.getcwd())
            self._csv_file = open(CSV_ROOT_PATH+self._file_name + dateN.strftime("%Y-%m-%d-%H-%M-%S") + ".csv", 'w')
            ligne = "heure ; pression (mb); température °C ; profondeur (m)"
            logging.debug(f"Ecriture CSV : {ligne}")
            self._csv_file.write(ligne + '\n')
            self._csv_file.flush()
            
            while not self._pause_event.isSet():
                pressStr = ""
                tempStr = ""
                profStr = ""
                if self._press_sensor_ok:
                    if self.pressure_sensor.read():
                        press = self.pressure_sensor.pressure()  # Default is mbar (no arguments)
                        pressStr = f'{press:.1f}'
                        temp = self.pressure_sensor.temperature()  # Default is degrees C (no arguments)
                        tempStr = f'{temp:.2f}'
                        prof=(press-1000)/100
                        profStr=f'{prof:2f}'
                vDate = datetime.now()
                date = datetime.now()
                vHeure = date.strftime("%H:%M:%S")
                ligne = f'{vHeure} ; {pressStr} ; {tempStr} ; {profStr}'
                try:
                    self._csv_file.write(ligne + '\n')
                    self._csv_file.flush()
                    
                except Exception as e:
                    logging.error(f"Error writing to CSV file: {e}")

                # Attendre le prochain enregistrement ou l'évènement d'arrêt.
                self._stopevent.wait(self._time_step)
            else:
                self._csv_file.close()
                logging.info("Fichier CSV fermé")
                self._continue_event.wait()
        logging.info("Thread CSV terminé") 
    
    
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
          
    def stop_thread(self):
        """positionne l'évènement qui va provoquer l'arrêt du thread"""
        self.stop = True
        self._stopevent.set()
        self._continue_event.set()
        self._pause_event.set()
