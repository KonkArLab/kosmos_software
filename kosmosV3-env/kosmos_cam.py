#!/usr/bin/python
# coding: utf-8
""" Camera KOSMOS
 D. Hanon 21 novembre 2020 """

from threading import Thread, Event
import subprocess
import logging
import picamera
import os
from kosmos_config import *


logging.basicConfig(level=logging.DEBUG)
#VIDEO_ROOT_PATH = os.path.join(USB_ROOT_PATH, os.listdir(USB_ROOT_PATH)[0], "Video")

class KosmosCam(Thread):
    """
    Classe dérivée de Thread qui gère l'enregistrement video.
    """
    def __init__(self, aConf: KosmosConfig):
        """ constructeur de la classe ... initialise les paramètres
            Parameters:
                Conf (KosmosConfig) : gestionaire de la config
                aDate date : utilistée juste pour fixer le nom du fichier vidéo
        Dans le fichier de configuration :
            SETT_VIDEO_RESOLUTION_X : la résolution horizontale
            SETT_VIDEO_RESOLUTION_Y : la résolution verticale
            SETT_VIDEO_PREVIEW : si 1 : Lance la fenêtre de preview (utile en debug)
            SETT_VIDEO_FILE_NAME : le nom du fichier (sans extension)
            SETT_RECORD_TIME : le temps d'enregistrement en secondess.
        """
        Thread.__init__(self)
        self._Conf = aConf
        # Résolution horizontale
        self._X_RESOLUTION = aConf.get_val_int("SETT_VIDEO_RESOLUTION_X")
        # Résolution verticale
        self._Y_RESOLUTION = aConf.get_val_int("SETT_VIDEO_RESOLUTION_Y")
        #Framerate camera
        self._FRAMERATE = aConf.get_val_int("SETT_FRAMERATE")
        # si 1 : Lance la fenêtre de preview (utile en debug)
        self._PREVIEW = aConf.get_val_int("SETT_VIDEO_PREVIEW")
        self._camera = picamera.PiCamera()
        # (1024,768)
        self._camera.resolution = (self._X_RESOLUTION, self._Y_RESOLUTION)
        self._camera.framerate = self._FRAMERATE
        #self._camera.awb_mode='off'
        #self._camera.awb_gains=(2,3)
        self._record_time = aConf.get_val_int("SETT_RECORD_TIME")
        self._end = False
        self._start_again = Event()
        self.MODE= aConf.get_val_int("SETT_MODE")
    
    """
    def getRecordTime(self) -> int: #utilisation dans main en commentaire - a garder?
        return self._record_time
    """
    
    def convert_to_mp4(self, input_file, path):
        output_file = os.path.splitext(input_file)[0] + '.mp4'
        full_input_path = os.path.join(path, input_file)
        full_output_path = os.path.join(path, output_file) 

        if not os.path.exists(full_input_path):
            print(f"Input file '{full_input_path}' not found.")
            return
        
        try:
            subprocess.run(['sudo', 'ffmpeg', '-probesize', '2G', '-i', full_input_path, '-c', 'copy', full_output_path, '-loglevel', 'warning'])
            print("Conversion successful !")

            os.remove(full_input_path)
            print(f"Deleted input H.264 file: {input_file}")
        
        except subprocess.CalledProcessError as e:
            print("Error during conversion:", e, " !!!")
       
    
    def run(self):
        """  Lance l'enregistrement vidéo
        vers un fichier donné dans le fichier de conf (SETT_VIDEO_FILE_NAME)
        pour un temps donné dans le fichier de conf (SETT_RECORD_TIME)
        """
        
        while not self._end:
            self._base_name = self._Conf.get_val("SETT_VIDEO_FILE_NAME") + '_' + self._Conf.get_date()
            self._file_name = self._base_name + '.h264'
            if (self.MODE==0) :
                logging.info(f"enregistrement caméra lancé pour : {self._record_time} secondes")
            if self._PREVIEW == 1:
                self._camera.start_preview(fullscreen=False, window=(50, 50, 640, 480))
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            os.chdir("media")
            os.chdir(os.listdir("/home")[0]) 
            os.chdir(os.listdir(os.getcwd())[0])  
            if os.getenv("Video"): 
                os.chdir("Video")
            else:
                if not os.path.exists("Video"): 
                    os.mkdir("Video")
                os.chdir("Video")
                
            self._camera.start_recording(self._file_name)
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            os.chdir("..")
            os.chdir("home")
            os.chdir(os.listdir("/home")[0])
            os.chdir("kosmos_software")
            os.chdir("kosmosV3-env")

            self._camera.wait_recording(self._record_time)
            logging.info(f"Fin de l'enregistrement video {self._file_name}")
            
            input_video = self._file_name
            #path = VIDEO_ROOT_PATH
            #self.convert_to_mp4(input_video, path)
            
            self._start_again.wait()
            self._start_again.clear()
    
    def do_capture(self, fichier) :
        #a modifier pour correction RGB
        self._camera.capture(fichier) #saved in "/home/kosmosenib/Images"
        print("Capture reussie")
    
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        if self._camera.recording is True:
            # terminer l'enregistrement video
            if self._PREVIEW == 1:
                self._camera.stop_preview()
            self._camera.stop_recording()

    def closeCam(self):
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.close()

    def restart(self):
        """démarre ou redémarre le thread"""
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()
    
    #Fonction(s) non utilisée(s) - commenter le 18/07/23 par Ion
    """
    def get_raw_file_name(self) -> str:
        # retourne le nom du fichier h264 
        return self._file_name

    def get_mepg_file(self) -> str:
        #retourne le nom du fichier mp4
        return self._base_name + '.mp4'

    def convert_to_mepg(self) -> bool:
        #Conversion en mpeg 4.
        #Utilise la commande x264 dans le repertoire courant.
        #Génère un fichier de même nom mais à l'extension mp4.
        #La conversion est assez gourmande en temps ...
        #Ce n'est certainement pas à faire sur la caméra mais au labo !
        #Test le 4/12/2020 ... ça chauffe ! essayer avec juste os ...?
        #... non pas génial ... ça chauffe même sans le python (en ligne de commande)!
        
        mpegName = self.get_mepg_file()
        com = f"x264 {self._file_name} -o {mpegName}"
        logging.debug(com)
        ret1 = os.system(com)
        if ret1 == 0:
            return True
        return False
        # result = subprocess.run(["x264", self._file_name, "-o", mpegName], capture_output=True)
        # if result.returncode == 0:
        
    """
