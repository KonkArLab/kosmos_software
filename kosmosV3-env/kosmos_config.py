#!/usr/bin/python
# coding: utf-8

import logging
import configparser
import os.path
import subprocess
from datetime import datetime
import json



#Arborescence USB
USB_ROOT_PATH = "/media/"+(os.listdir("/home")[0])
USB_NAME = os.listdir(USB_ROOT_PATH)[0]
USB_INSIDE_PATH = USB_ROOT_PATH+"/"+USB_NAME+"/"

# Arborescence Picam
ROOT_PATH = "/home/"+os.listdir("/home")[0]+"/"
LOG_PATH = ROOT_PATH+"logfile_kosmos/"
GIT_PATH = ROOT_PATH+"kosmos_software/"
WORK_PATH = GIT_PATH+"kosmosV3-env/"

# Fichier config et sections associées
CONF_FILE = "kosmos_config.ini"
TERRAIN_SECTION = "KOSMOS-terrain"
DEBUG_SECTION = "KOSMOS-debug"

# Fichier system et sections associées
SYSTEM_FILE = "kosmos_system.ini"
SYSTEM_SECTION = "KOSMOS-system"
INCREMENT_SECTION = "KOSMOS-increment"


class KosmosConfig:
    """
    Gestion des paramètres et leur lecture depuis le fichier .ini
    Ce fichier pouvant etre sur la clef ou dans le repertoire courant
    """
    
    def __init__(self):
        logging.debug("Lecture kosmos_config.ini")        
        subprocess.run(["sudo", "cp", "-n", GIT_PATH+CONF_FILE,USB_INSIDE_PATH+CONF_FILE])
        self._config_path=USB_INSIDE_PATH+CONF_FILE
        self.config = configparser.ConfigParser()
        self.config.read(self._config_path)
        logging.info("kosmos_config.ini lu sur clé usb")
        
        logging.debug("Lecture kosmos_system.ini")        
        subprocess.run(["sudo", "cp", "-n", GIT_PATH+SYSTEM_FILE,ROOT_PATH+SYSTEM_FILE])
        self._system_path=ROOT_PATH+SYSTEM_FILE
        self.system = configparser.ConfigParser()
        self.system.read(self._system_path)
        logging.info("kosmos_system.ini lu dans home")
               
        # Création Dossier Campagne si non existant               
        CAMPAGNE_FILE = self.get_date_YMD() + '_' + self.system.get(SYSTEM_SECTION,"00_name") + '_' + self.config.get(TERRAIN_SECTION,"22_CSV_campagne") + '_' + self.config.get(TERRAIN_SECTION,"21_CSV_zone") 
        os.chdir(USB_INSIDE_PATH)            
        if not os.path.exists(CAMPAGNE_FILE):
            os.mkdir(CAMPAGNE_FILE)
        self.CAMPAGNE_PATH = USB_INSIDE_PATH + CAMPAGNE_FILE + "/"
        os.chdir(WORK_PATH)
        
        # Creation du CSV info station si non existant
        with open(GIT_PATH+'infoStationList.json') as f:
            self.infoStationList = json.load(f)
        
        print(self.infoStationList)
        
    def get_date_Y(self) -> str:
        date = datetime.now()
        Y=date.year-2000
        return f'{Y:02}'    
        
    def get_date_YMD(self) -> str:
        date = datetime.now()
        Y=date.year-2000
        m=date.month
        d=date.day
        return f'{Y}{m:02}{d:02}'
       
    def get_date_YMDHM(self) -> str:
        date = datetime.now()
        Y=date.year
        m=date.month
        d=date.day
        H=date.hour
        M=date.minute
        return f'{Y}{m:02}{d:02}{H:02}{M:02}'

    def get_date_HMS(self) -> str:
        """Retourne la date formatée en string"""
        date = datetime.now()
        H=date.hour
        M=date.minute
        S=date.second
        return f'{H:02}h{M:02}m{S:02}s'
    
    def get_date(self) -> str:
        """Retourne la date formatée en string"""
        date = datetime.now()
        return date.strftime("%Y-%m-%d-%H-%M-%S")
    
    def get_val_int(self, aKey, aSection):
        """
        Retourne la valeur d'un paramètre dont le nom est passé en argument.
        Parameters:
            aKey (str): nom du paramètre de config recherché
            aSection (str) : section du fichier ini dans le quel on recherche
                    le paramètre de config.
        """
        return self.config.getint(aSection, aKey)
    
    def get_val(self, aKey, aSection):
        """
        Retourne la valeur d'un paramètre dont le nom est passé en argument.
        Parameters:
            aKey (str): nom du paramètre de config recherché
            aSection (str) : section du fichier ini dans le quel on recherche
                    le paramètre de config.
        """
        return self.config.get(aSection, aKey)
    
    def set_val(self,aKey,aValue ,aSection=TERRAIN_SECTION):
        self.config.set(aSection, aKey,str(aValue))
        
    def update_file(self):
        with open(self._config_path, 'w') as configfile:
            self.config.write(configfile)
            
    def update_system(self):
        with open(self._system_path, 'w') as systemfile:
            self.system.write(systemfile)
            
            
    def add_line(self,csv_file,ligne):
        try:
            with open(csv_file,'a') as csv_variable:
                csv_variable.write(ligne + '\n')
                csv_variable.flush() 
                csv_variable.close()
        except:
            logging.info('Problème écriture dans le CSV Event')