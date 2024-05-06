#!/usr/bin/python
# coding: utf-8
""" Camera KOSMOS
 D. Hanon 21 novembre 2020 """

from threading import Thread, Event
import subprocess
import logging
#import picamera
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2,Preview,MappedArray
import cv2


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
             38_PICAM_timestamp : présence d'une incrustation avec le temps en haut à gauche
        """
        
        # On restreint les messages 
        Picamera2.set_logging(Picamera2.ERROR)
       
        Thread.__init__(self)
        self._Conf = aConf    
        # Résolutions horizontale
        self._X_RESOLUTION = aConf.get_val_int("31_PICAM_resolution_x")
        self._Y_RESOLUTION = aConf.get_val_int("32_PICAM_resolution_y")
        
        # Framerate et frameduration camera
        self._FRAMERATE=aConf.get_val_int("34_PICAM_framerate")
        self._FRAMEDURATION = int(1/self._FRAMERATE*1000000)
        
        # Preview ou non
        self._PREVIEW = aConf.get_val_int("33_PICAM_preview")
        
        # si 1 : conversion mp4
        self._CONVERSION = aConf.get_val_int("36_PICAM_conversion_mp4")
        
        # A clarifier
        self._AWB = aConf.get_val_int("37_PICAM_AWB")
        self._record_time = aConf.get_val_int("35_PICAM_record_time")

        # Booléens pour les évènements
        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation Camera
        self._camera=Picamera2()
        self._video_config=self._camera.create_video_configuration()
        self._video_config['main']['size']=(self._X_RESOLUTION,self._Y_RESOLUTION)
        self._video_config['controls']['FrameDurationLimits']=(self._FRAMEDURATION,self._FRAMEDURATION)
        self._camera.configure(self._video_config)
        self._camera.start() #A noter que le Preview.NULL démarre également 
        logging.info("Camera démarrée")
        
        # Instanciation Encoder
        self._encoder=H264Encoder(framerate=self._FRAMERATE, enable_sps_framerate=True,bitrate=10000000)
                
        #Creation du dossier Video dans la clé usb si pas déjà présent.
        os.chdir(USB_INSIDE_PATH)            
        if not os.path.exists("Video"):
            os.mkdir("Video")
        os.chdir(WORK_PATH)
        
        # Appel heure pour affichage sur la frame
        if aConf.get_val_int("38_PICAM_timestamp") == 1:
            self._camera.pre_callback = self.apply_timestamp

    
    def apply_timestamp(self,request):
        #Time stamp en haut à gauche de la video
        timestamp = time.strftime("%Y-%m-%d %X")
        colour = (0, 255, 0)
        origin = (0, 30)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)
      
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
      
    def initialisation_awb(self):
        if self._AWB == 0:
            logging.info('Gains AWB ajustés par Rpi')
            self._camera.controls.AwbMode=0
        else:
            logging.info('Gains AWB fixés par Rpi')
            self._camera.set_controls({'AwbEnable': False})
            self._camera.set_controls({'ColourGains': (5, 0.2)})
        
    def run(self):       
        while not self._end:
            i=0
            self._base_name = self._Conf.get_val("30_PICAM_file_name") + '_' + self._Conf.get_date()
           
            while self._boucle == True:                
                self._file_name = self._base_name +'_' + '{:04.0f}'.format(i) + '.h264'
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                self._output=VIDEO_ROOT_PATH+self._file_name
                
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #éteint le Preview.NULL
                    self._camera.start_preview(Preview.QTGL,width=800,height=600)
                
                # Bloc d'enregistrement/encodage à proprement parler
                self._camera.start_encoder(self._encoder,self._output)
                time_debut=time.time()
                delta_time=0
                while self._boucle == True and delta_time < self._record_time:
                    delta_time = time.time()-time_debut
                    time.sleep(0.25)    
                self._camera.stop_encoder()
                # Fin de l'encodage
                               
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #stop .QTGL
                    self._camera.start_preview(Preview.NULL) #redemarrage .NULL
                    
                logging.info(f"Fin de l'enregistrement video {self._file_name}")
                
                # Conversion mp4 si demandée
                self.convert_to_mp4(self._file_name, VIDEO_ROOT_PATH)
                i=i+1
            self._start_again.wait()
            self._start_again.clear()            
        logging.info('Thread Camera terminé')       

    
    
    def do_capture(self) :
        self._camera.capture_file(LOG_PATH+'test.jpg')#,use_video_port=True,resize=(int(self._X_RESOLUTION/4),int(self._Y_RESOLUTION/4)))
        logging.debug("Capture reussie")
    
    
    '''  
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
    '''    
        
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle=False
            
    def closeCam(self):
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.stop()
        logging.info("Caméra arrêtée")
        self._camera.close()
        logging.info("Caméra éteinte")

    def restart(self):
        """démarre ou redémarre le thread"""
        self._boucle=True
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()
    
