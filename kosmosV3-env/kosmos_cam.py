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
from PIL import Image
import numpy as np
import time
import RPi.GPIO as GPIO  # Importe la bibliotheque pour contrôler les GPIOs

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
             37_PICAM_AWB : Règle l'ajustemetn de paramètres awb pour controle couleur : 0 picam classique, 1 awb fixé, 2 awb ajusté
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
        self._AWB = aConf.get_val_int("37_PICAM_AWB")

        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation Camera
        self._camera = picamera.PiCamera()
        self._camera.resolution = (self._X_RESOLUTION, self._Y_RESOLUTION)  # (1024,768)
        self._camera.framerate = self._FRAMERATE
        #if self._AWB == 0 or self._AWB ==2: # AWB ajustement Picam (0) ou Fait Maison (2) 
            #self._camera.awb_mode='auto'
        
        
       
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
            self._camera.start_preview(fullscreen=False, window=(50, 50, int(self._X_RESOLUTION/4),int(self._Y_RESOLUTION/4)))
            
    def stop_preview(self):
        if self._PREVIEW == 1:
            self._camera.stop_preview()
    
    def initialisation_awb(self):
        if self._AWB == 0:
            logging.info('Gains AWB ajustés par Rpi')
            self._camera.awb_mode='auto'
        else:
            self._camera.start_preview(fullscreen=False, window=(50, 50, int(self._X_RESOLUTION/4),int(self._Y_RESOLUTION/4)))
            time.sleep(1)
            g=self._camera.awb_gains
            logging.info(g)
            self._camera.awb_mode='off'
            self._camera.awb_gains=g#(0.5,0.5)
            self.drc_strength='off'
            time.sleep(1)
            self._camera.stop_preview()
            if self._AWB == 1:
                logging.info('Gains AWB calculés en surface puis fixés')
            if self._AWB == 2:
                logging.info('Gains AWB calculés en surface puis ajustés pour histogramme centré')
        
        
    def run(self):       
        while not self._end:
            i=0
            self._base_name = self._Conf.get_val("30_PICAM_file_name") + '_' + self._Conf.get_date()
            while self._boucle == True:                
                if self._camera.recording is True:
                    self._camera.stop_recording()
                self._file_name = self._base_name +'_' + '{:04.0f}'.format(i) + '.h264'
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                self._camera.start_recording(VIDEO_ROOT_PATH+self._file_name)
                #self._camera.annotate_text=str(self._camera.awb_gains[0])+' ' +str(self._camera.awb_gains[1])
                if self._AWB == 2:
                    time.sleep(0.1)
                    self.adjust_histo(1,1,0.05)
                self._camera.wait_recording(self._record_time)
                logging.info(f"Fin de l'enregistrement video {self._file_name}")
                # Conversion mp4 si demandée
                self.convert_to_mp4(self._file_name, VIDEO_ROOT_PATH)
                i=i+1                               
            self._start_again.wait()
            self._start_again.clear()            
        logging.info('Thread Camera terminé')       

    
    
    def do_capture(self) :
        #a modifier pour correction RGB
        self._camera.capture(LOG_PATH+'test.jpg',use_video_port=True,resize=(int(self._X_RESOLUTION/4),int(self._Y_RESOLUTION/4)))
        logging.debug("Capture reussie")
        
    def histo(self):
        img= Image.open(LOG_PATH+'test.jpg')
        r,g,b = img.split()
        xx=np.linspace(0,255,256)
        r_med= sum(r.histogram()*xx)/sum(r.histogram())
        g_med= sum(g.histogram()*xx)/sum(g.histogram())
        b_med= sum(b.histogram()*xx)/sum(b.histogram())    
        return r_med,g_med,b_med
        
    def adjust_histo(self,rh,bh,tolerance):
        self._camera.awb_mode='off'
        red=self._camera.awb_gains[0]
        blue=self._camera.awb_gains[1]       
        self.do_capture()
        time.sleep(0.1)
        HH=self.histo()
        rr=HH[0]
        gg=HH[1]
        bb=HH[2]
        coef_convergence=0.9 # pas d'ajustement des gains awb
        i=0 # compteur initialisé pour sortir de la boucle si trop long
        imax=10 # nombre d'itérations max avant retour à référence
        while i<imax and (rr/gg > rh+tolerance or rr/gg < rh-tolerance or bb/gg > bh+tolerance or bb/gg < bh-tolerance) :
            ratioR=rr/gg
            ratioB=bb/gg
            red = red + coef_convergence*(rh-ratioR)
            blue = blue + coef_convergence*(bh-ratioB)
            # On threshold pour rester dans les clous 0&8
            a=min(7.88,red)
            red=max(0.5,a)
            b=min(7.8,blue)
            blue=max(0.5,b)
            #MàJ
            self._camera.awb_gains=(red,blue)
            self.do_capture()
            time.sleep(0.1)
            HH=self.histo()
            rr=HH[0]
            gg=HH[1]
            bb=HH[2]
            i=i+1
        else:
            if i < imax:
                logging.info('Coefficients AWB trouvés pour histogramme ajusté')
            else:
                self._camera.awb_mode='auto'
                logging.info('Coefficients AWB non trouvés, retour en mode awb_auto')
            os.remove(LOG_PATH+'test.jpg')
         
    
    
    
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle=False
        if self._camera.recording is True:
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
    
