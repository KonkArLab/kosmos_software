#!/usr/bin/python
# coding: utf-8

import logging
import configparser
import os.path
import subprocess
from datetime import datetime


CONF_FILE = "kosmos_config.ini"
USB_ROOT_PATH = "/media/"+(os.listdir("/home")[0])
USB_NAME=os.listdir(USB_ROOT_PATH)[0]
USB_INSIDE_PATH = USB_ROOT_PATH+"/"+USB_NAME+"/"

VIDEO_ROOT_PATH=USB_INSIDE_PATH+"Video/"
CSV_ROOT_PATH=USB_INSIDE_PATH+"CSV/"

LOG_PATH="/home/"+os.listdir("/home")[0]+"/logfile_kosmos/"
GIT_PATH="/home/"+os.listdir("/home")[0]+"/kosmos_software/"
WORK_PATH=GIT_PATH+"kosmosV3-env/"

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
            
            
            
    '''
    def copy_file(self, aFileName: str) -> bool:
        """ copy le fichier vers la clef USB """
        logging.debug(f"cp {aFileName} {self._usb_path}")
        if self._usb_path != "":
            result = subprocess.run(["sudo", "cp", aFileName, self._usb_path],
                                    capture_output=True)
            if result.returncode == 0:
                return True
        return False
       
    def print_all(self):
        """Affiche le fichier de configuration (pour debug). """
        # Parcourt des sections
        for sec in self.config.sections():
            logging.info("section : {}".format(sec))
            # parcourir parametres et valeurs
            for name, value in self.config.items(sec):
                logging.info("{} = {}".format(name, value))

    
    def rm_file(self, aFileName: str) -> bool:
        """ Supprime le fichier dans le répertoire courant
        NE PAS OUBLIER DE LE COPIER la clef USB """
        logging.debug(f"rm {aFileName}")
        result = subprocess.run(["rm", aFileName],
                                capture_output=True)
        if result.returncode == 0:
            return True
        return False

    def moove_file(self, aFileName: str) -> bool:
        """ Déplacer le fichier après la copie la clef USB """
        if self.copy_file(aFileName) is True:
            if self.rm_file(aFileName):
                logging.info(f"Le fichier {aFileName} a bien été déplacé vers la clef USB.")
                return True
        logging.warning(f"Impossible de déplacer le {aFileName} vers la clef USB.")
        return False
    '''