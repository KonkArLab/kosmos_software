#!/usr/bin/python
# coding: utf-8

from threading import Thread
from threading import Event
import time
import serial
import logging

class GPS(Thread):
    def __init__(self):
        
        Thread.__init__(self)
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.1)
        self.ser.close()
        self.ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=0.1)
        self._pause_event = Event()
        self._continue_event = Event()
        self._t_stop = False 
        
        self.latitude = 0.
        self.longitude = 0.
                
    def init(self):
        bool_gps = False  
        testA = self.ser.inWaiting()
        time.sleep(1)
        testB = self.ser.inWaiting()
        if testA != testB:
            bool_gps = True  
        return bool_gps
        
    def card2sign(self,card):
        a = 0.0
        if card == b'N' or card == b'E':
            a = 1.0
        else:
            a = -1.0
        return a 
     
    def run(self):
        while not self._t_stop:    
            while not self._pause_event.isSet():                
                rcv = self.ser.readline()
                rcvsplit = rcv.split(b',')               
                if rcvsplit[0] == b'$GNGGA':                    
                    LATGPS = rcvsplit[2:4]                    
                    if LATGPS[0] != b'':
                        logging.debug("Latitude captée")
                        self.latitude = (self.card2sign(LATGPS[1])*(int(float(LATGPS[0])/100) + ((float(LATGPS[0])/100) % 1)*100/60))
                    else:
                        logging.debug("Latitude non captée")
                        self.latitude = 0.
                    
                    LONGGPS = rcvsplit[4:6]
                    if LONGGPS[0] != b'':    
                        self.longitude = (self.card2sign(LONGGPS[1])*(int(float(LONGGPS[0])/100) + ((float(LONGGPS[0])/100) % 1)*100/60))
                    else:
                        self.longitude = 0.   
        
                time.sleep(0.01)
            else:
                self._continue_event.wait()
        self.arret_complet() 
     
    def get_latitude(self):
        return f'{self.latitude:.5f}'
    
    def get_longitude(self):
        return f'{self.longitude:.5f}'
       
    def arret_complet(self):
        self.ser.close()
        logging.info('GPS coupé')
        
    def stop_thread(self):
        """positionne l'évènement qui va provoquer l'arrêt du thread"""
        self._t_stop = True
        self._continue_event.set()
        self._pause_event.set()
  
    def pause(self): # pas utilisé dans le code
        """suspend le thread pour pouvoir le redémarrer."""
        self._continue_event.clear()
        self._pause_event.set()

    def restart(self): # pas utilisé dans le code
        """Relance le thread"""
        if self.is_alive():
            self._pause_event.clear()
            self._continue_event.set()
        else:           
            self.start()
    