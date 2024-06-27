#!/usr/bin/python
# coding: utf-8

import logging
import configparser
import os.path
import subprocess
from datetime import datetime


CONF_FILE = "kosmos_config.ini"

#Arborescence USB
USB_ROOT_PATH = "/media/"+(os.listdir("/home")[0])
USB_NAME = os.listdir(USB_ROOT_PATH)[0]
USB_INSIDE_PATH = USB_ROOT_PATH+"/"+USB_NAME+"/"

VIDEO_ROOT_PATH = USB_INSIDE_PATH+"Video/"
CSV_ROOT_PATH = USB_INSIDE_PATH+"CSV/"

# Arborescence Picam
LOG_PATH = "/home/"+os.listdir("/home")[0]+"/logfile_kosmos/"
GIT_PATH = "/home/"+os.listdir("/home")[0]+"/kosmos_software/"
WORK_PATH = GIT_PATH+"kosmosV3-env/"

BASIC_SECTION = "KOSMOS"   

class KosmosConfig:
    """
    Gestion des paramètres et leur lecture depuis le fichier .ini
    Ce fichier pouvant etre sur la clef ou dans le repertoire courant
    """
    
    def __init__(self):
        logging.debug("Lecture kosmos_config.ini")        
        subprocess.run(["sudo", "cp", "-n", GIT_PATH+CONF_FILE,USB_INSIDE_PATH+CONF_FILE])
        self._file_path=USB_INSIDE_PATH+CONF_FILE
        self.config = configparser.ConfigParser()
        self.config.read(self._file_path)
        logging.info("kosmos_config.ini lu sur clé usb")
        
        # Création Dossier Campagne si non existant
        CAMPAGNE_FILE = self.get_val("22_CSV_campagne")+self.get_date_Yms()
        os.chdir(USB_INSIDE_PATH)            
        if not os.path.exists(CAMPAGNE_FILE):
            os.mkdir(CAMPAGNE_FILE)
        self.CAMPAGNE_PATH = USB_INSIDE_PATH + CAMPAGNE_FILE + "/"
        os.chdir(WORK_PATH)

    def get_date_Yms(self) -> str:
        """Retourne la date formatée en string"""
        date = datetime.now()
        Y=date.year-2000
        m=date.month
        d=date.day
        return f'{Y:02}{m:02}{d:02}'

    def get_date_HMS(self) -> str:
        """Retourne la date formatée en string"""
        date = datetime.now()
        H=date.hour
        M=date.minute
        S=date.second
        return f'{H:02}{M:02}{S:02}'
    
    def get_date(self) -> str:
        """Retourne la date formatée en string"""
        date = datetime.now()
        return date.strftime("%Y-%m-%d-%H-%M-%S")
    
    def get_val_int(self, aKey, aSection=BASIC_SECTION):
        """
        Retourne la valeur d'un paramètre dont le nom est passé en argument.
        Parameters:
            aKey (str): nom du paramètre de config recherché
            aSection (str) : section du fichier ini dans le quel on recherche
                    le paramètre de config.
        """
        return self.config.getint(aSection, aKey)
    
    def get_val(self, aKey, aSection=BASIC_SECTION):
        """
        Retourne la valeur d'un paramètre dont le nom est passé en argument.
        Parameters:
            aKey (str): nom du paramètre de config recherché
            aSection (str) : section du fichier ini dans le quel on recherche
                    le paramètre de config.
        """
        return self.config.get(aSection, aKey)
    
    def set_val(self,aKey,aValue ,aSection=BASIC_SECTION):
        self.config.set(aSection, aKey,str(aValue))
        
    def update_file(self):
        with open(self._file_path, 'w') as configfile:
            self.config.write(configfile)
            