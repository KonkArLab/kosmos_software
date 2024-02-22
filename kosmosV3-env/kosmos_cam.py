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
             31_PICAM_resolution_x : la résolution horizontale
             32_PICAM_resolution_y : la résolution verticale
             34_PICAM_framerate  : framerate
             33_PICAM_preview : si 1 : Lance la fenêtre de preview (utile en debug)
             30_PICAM_file_name  : le nom du fichier (sans extension)
             35_PICAM_record_time : le temps d'enregistrement en secondes.
             36_PICAM_conversion_mp4 : 1 si on souhaite effectuer la conversion juste après l'acquisition

        """
        Thread.__init__(self)
        self._Conf = aConf    
        # Résolution horizontale
        self._X_RESOLUTION = aConf.get_val_int("31_PICAM_resolution_x")
        # Résolution verticale
        self._Y_RESOLUTION = aConf.get_val_int("32_PICAM_resolution_y")
        #Framerate camera
        self._FRAMERATE = aConf.get_val_int("34_PICAM_framerate")
        # si 1 : Lance la fenêtre de preview (utile en debug)
        self._PREVIEW = aConf.get_val_int("33_PICAM_preview")
        self._record_time = aConf.get_val_int("35_PICAM_record_time")
        # si 1 : conversion mp4
        self._CONVERSION = aConf.get_val_int("36_PICAM_conversion_mp4")

        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation Camera
        self._camera = picamera.PiCamera()
        self._camera.resolution = (self._X_RESOLUTION, self._Y_RESOLUTION)  # (1024,768)
        self._camera.framerate = self._FRAMERATE
        #self._camera.awb_mode='off'
        #self._camera.awb_gains=(2,3)
       
        os.chdir(USB_INSIDE_PATH)            
        if not os.path.exists("Video"):
            #Creation du fichier Video dans la clé usb si pas déjà présent.
            os.mkdir("Video")
        os.chdir(WORK_PATH)
    
    def convert_to_mp4(self, input_file, path):
        if self._CONVERSION == 1:
            #Conversion h264 vers mp4 puis effacement du .h264
            output_file = os.path.splitext(input_file)[0] + '.mp4'
            full_input_path = os.path.join(path, input_file)
            full_output_path = os.path.join(path, output_file) 

            if not os.path.exists(full_input_path):
                logging.error(f"Input file '{full_input_path}' not found.")
                return
                
            try:
                subprocess.run(['sudo', 'ffmpeg', '-probesize', '2G', '-i', full_input_path, '-c', 'copy', full_output_path, '-loglevel', 'warning'])
                logging.info("Conversion successful !")
                os.remove(full_input_path)
                logging.debug(f"Deleted input H.264 file: {input_file}")
                
            except subprocess.CalledProcessError as e:
                logging.error("Error during conversion:", e, " !!!")
        else:
            logging.info("Pas de conversion mp4 demandée")
            
    def run_preview(self):
        """ Lance le preview"""
        if self._PREVIEW == 1:
            self._camera.start_preview(fullscreen=False, window=(50, 50, 640, 480))
            
    def stop_preview(self):
        if self._PREVIEW == 1:
            self._camera.stop_preview()
            
    def run(self):
        """  Lance l'enregistrement vidéo
        vers un fichier donné dans le fichier de conf (30_PICAM_file_name)
        pour un temps donné dans le fichier de conf (35_PICAM_record_time)
        """
        
        while not self._end:
            i=0
            self._base_name = self._Conf.get_val("30_PICAM_file_name") + '_' + self._Conf.get_date()
            while self._boucle == True:                
                if self._camera.recording is True:
                    self._camera.stop_recording()                  
                self._file_name = self._base_name +'_' + '{:04.0f}'.format(i) + '.h264'
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                self._camera.start_recording(VIDEO_ROOT_PATH+self._file_name)            
                self._camera.wait_recording(self._record_time)
                logging.info(f"Fin de l'enregistrement video {self._file_name}")
                # Conversion mp4 si demandée
                self.convert_to_mp4(self._file_name, VIDEO_ROOT_PATH)
                i=i+1                               
            self._start_again.wait()
            self._start_again.clear()            
        logging.info('Thread Camera terminé')       

    
    
    def do_capture(self, fichier) :
        #a modifier pour correction RGB
        self._camera.capture(fichier)
        logging.info("Capture reussie")
    
 
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle=False
        if self._camera.recording is True:
            print('Arrêt prématuré')
            self._camera.stop_recording()
        
        
    def closeCam(self):
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.close()

    def restart(self):
        """démarre ou redémarre le thread"""
        self._boucle=True
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()
    
