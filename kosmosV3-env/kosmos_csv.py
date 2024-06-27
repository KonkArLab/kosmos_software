#!/usr/bin/python
# coding: utf-8
from datetime import datetime

from threading import Thread
from threading import Event
import logging
import os
import time

import ms5837  # librairie du capteur de pression et temperature
import serial # librairie pour le GPS


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
        
        
        # Initialisation GPS
        self._gps_ok = False
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=5)
        self._test_read = self.ser.readline()
        if not self._test_read == b'' :
            self._gps_ok = True
            logging.info("GPS OK")
        else:
            logging.error("Erreur d'initialisation du port série GPS")
        
                
        # Booléen de capture
        self.stop = False

    def card2sign(self,card):
        a = 0.0
        if card == b'N' or card == b'E':
            a = 1.0
        else:
            a = -1.0
        return a


    def run(self):
        """Ecriture des données sur le fichier CSV"""
        while self.stop is False:
            logging.info("Fichier CSV ouvert")
            dateN = datetime.now()
            self._csv_file = open("TemperaturePressionGPS.csv", 'w')
            ligne = "heure ; pression (mb); température °C ; profondeur (m), LAT (°), LONG (°)"
            logging.debug(f"Ecriture CSV : {ligne}")
            self._csv_file.write(ligne + '\n')
            self._csv_file.flush()
            
            while not self._pause_event.isSet():       

                vDate = datetime.now()
                date = datetime.now()
                vHeure = date.strftime("%H:%M:%S")
                
                # Bloc TP
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
            
                #Bloc GPS
                LAT = ""
                LONG = ""
                if self._gps_ok:
                    time_debut=time.time()
                    delta_time=0
                    while delta_time < 1.01:
                        delta_time = time.time()-time_debut
                        self._rcv = self.ser.readline()
                        self._rcvsplit = self._rcv.split(b',')
                        if self._rcvsplit[0] == b'$GNGGA':
                            self._LATGPS = self._rcvsplit[2:4]
                            if self._LATGPS[0] != b'':
                                LAT = f'{(self.card2sign(self._LATGPS[1])*(int(float(self._LATGPS[0])/100) + ((float(self._LATGPS[0])/100) % 1)*100/60)):.5f}'
                            else:
                                LAT = ""
                            self._LONGGPS = self._rcvsplit[4:6]
                            if self._LONGGPS[0] != b'':    
                                LONG = f'{(self.card2sign(self._LONGGPS[1])*(int(float(self._LONGGPS[0])/100) + ((float(self._LONGGPS[0])/100) % 1)*100/60)):.5f}'
                            else:
                                LONG = ""
                        #elif self._rcvsplit[0] == b'$GNZDA':
                        #    self._HeureGPS = self._rcvsplit[1]
                        #    self._DateGPS = self._rcvsplit[2:5]
                        else:
                            pass
                        time.sleep(0.01)
                
                # Ecriture de la ligne
                ligne = f'{vHeure} ; {pressStr} ; {tempStr} ; {profStr} ; {LAT} ; {LONG}'
                try:
                    self._csv_file.write(ligne + '\n')
                    self._csv_file.flush()                    
                except Exception as e:
                    logging.error(f"Error writing to CSV file: {e}")

                # Attendre le prochain enregistrement ou l'évènement d'arrêt.
                self._stopevent.wait(self._time_step-1.01)
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
        self.ser.close()
        self.stop = True
        self._stopevent.set()
        self._continue_event.set()
        self._pause_event.set()
