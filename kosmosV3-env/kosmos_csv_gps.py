#!/usr/bin/python
# coding: utf-8
from datetime import datetime

from threading import Thread
from threading import Event

import logging
import os
import time

"""Connexion série du module gps"""
import serial
import serial.tools.list_ports as stlp

from kosmos_config import *

class kosmosCSV_GPS(Thread):
    """Classe dérivée de Thread qui gère l'enregistrement du CSV_GPS"""

    def __init__(self, aConf: KosmosConfig):
        """Constructeur de la classe kosmosCSV_GPS
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
        
        self.__step = aConf.get_val_int("20_CSV_step_time")
        self._file_name = aConf.get_val("21_CSV_file_name") + "_GPS_"
        
        os.chdir(USB_INSIDE_PATH)
        if not os.path.exists("CSV"): 
                os.mkdir("CSV")
        os.chdir(WORK_PATH)

        self._gps_ok = False
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=5)
        self._test_read = self.ser.readline()
        if not self._test_read == b'' :
            self._gps_ok = True
            logging.info("GPS OK")
        else:
            logging.error("Erreur d'initialisation du port série GPS")
        self.stop = False
    
    def card2sign(self,card):
        a = 0.0
        if card == b'N' or card == b'E':
            a = 1.0
        else:
            a = -1.0
        return a
    
    def run(self):
        """Ecriture des données sur le fichier CSV_GPS"""
        while self.stop is False:
            logging.info("Fichier CSV_GPS ouvert")
            dateN = datetime.now()
            self._csv_gps_file = open(CSV_ROOT_PATH+self._file_name + dateN.strftime("%Y-%m-%d-%H-%M-%S") + ".csv", 'w')
            
            ligne = "Date ; heure (GPS) ; LAT ; LONG "
            logging.debug(f"Ecriture CSV : {ligne}")
            self._csv_gps_file.write(ligne + '\n')
            self._csv_gps_file.flush()
            
            self.__tempo_GPS=2
            while not self._pause_event.isSet():
                self._DateGPS = 0.
                self._HeureGPS = 0.
                self._LAT = 0.
                self._LONG = 0.
                if self._gps_ok:
                    time_debut=time.time()
                    delta_time=0
                    while delta_time < self.__tempo_GPS:
                        delta_time = time.time()-time_debut
                        self._rcv = self.ser.readline()
                        self._rcvsplit = self._rcv.split(b',')
                        if self._rcvsplit[0] == b'$GNGGA':
                            self._LATGPS = self._rcvsplit[2:4]
                            if self._LATGPS[0] != b'':
                                self._LAT = self.card2sign(self._LATGPS[1])*(int(float(self._LATGPS[0])/100) + ((float(self._LATGPS[0])/100) % 1)*100/60)
                            else:
                                self._LAT = 0.
                            self._LONGGPS = self._rcvsplit[4:6]
                            if self._LONGGPS[0] != b'':    
                                self._LONG = self.card2sign(self._LONGGPS[1])*(int(float(self._LONGGPS[0])/100) + ((float(self._LONGGPS[0])/100) % 1)*100/60)
                            else:
                                self._LONG = 0.
                        elif self._rcvsplit[0] == b'$GNZDA':
                            self._HeureGPS = self._rcvsplit[1]
                            self._DateGPS = self._rcvsplit[2:5]
                        else:
                            pass
                        time.sleep(0.01)
                ligne = f'{self._HeureGPS} ; {self._DateGPS} ; {self._LAT:.5f} ; {self._LONG:.5f}'
                try:
                    self._csv_gps_file.write(ligne + '\n')
                    self._csv_gps_file.flush()
                    
                except Exception as e:
                    logging.error(f"Error writing to CSV file: {e}")

                # Attendre le prochain enregistrement ou l'évènement d'arrêt.
                self._stopevent.wait(self.__step-self.__tempo_GPS)
            else:
                self._csv_gps_file.close()
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
