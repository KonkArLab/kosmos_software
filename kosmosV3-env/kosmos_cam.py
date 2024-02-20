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
        self.MODE= aConf.get_val_int("00_SYSTEM_mode")
     
        self._end = False
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
    
    
    def convert_to_mp4(self, input_file, path):
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
       
    
    def run(self):
        """  Lance l'enregistrement vidéo
        vers un fichier donné dans le fichier de conf (30_PICAM_file_name)
        pour un temps donné dans le fichier de conf (35_PICAM_record_time)
        """
        
        while not self._end:  
            self._base_name = self._Conf.get_val("30_PICAM_file_name") + '_' + self._Conf.get_date()
            self._file_name = self._base_name + '.h264'
            '''
            if (self.MODE==0) :
                logging.info(f"enregistrement caméra lancé pour : {self._record_time} secondes")
            '''
            
            if self._PREVIEW == 1:
                self._camera.start_preview(fullscreen=False, window=(50, 50, 640, 480))
                        
            os.chdir(VIDEO_ROOT_PATH) 
            self._camera.start_recording(self._file_name)            
            self._camera.wait_recording(self._record_time)
            print(self._camera.recording)
            logging.info(f"Fin de l'enregistrement video {self._file_name}")
            
            input_video = self._file_name
            self.convert_to_mp4(input_video, VIDEO_ROOT_PATH)
            os.chdir(WORK_PATH)
            
            self._start_again.wait()
            self._start_again.clear()
            

    
    '''
    def do_capture(self, fichier) :
        #a modifier pour correction RGB
        self._camera.capture(fichier)
        print("Capture reussie")
    '''
 
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        if self._PREVIEW == 1:
            # Arrêt du preview
            self._camera.stop_preview()
        if self._camera.recording is True:
            print('tot')
            # terminer l'enregistrement video
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
    
