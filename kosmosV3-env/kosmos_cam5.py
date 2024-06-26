#!/usr/bin/python
# coding: utf-8
""" Camera KOSMOS
 D. Hanon 21 novembre 2020 """

from threading import Thread, Event
import subprocess
import logging
from picamera2.encoders import H264Encoder
from picamera2 import Picamera2,Preview,MappedArray,Metadata
import cv2

import os
from kosmos_config import *
from PIL import Image
import numpy as np
import time
import csv


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
        self._encoder=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)
                
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
        colour = (255, 255, 255)
        origin = (30, 1050)
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
        elif self._AWB == 1:
            logging.info('Gains AWB fixes')
            self._camera.controls.AwbMode=0
            time.sleep(0.5)
            self._camera.set_controls({'AwbEnable': False})
        elif self._AWB == 2:
            logging.info('Gains AWB ajustés par Algo Maison')
            self._camera.controls.AwbMode=0
            time.sleep(0.5)
            self._camera.set_controls({'AwbEnable': False})
            #self._camera.set_controls({'ColourGains': (5, 0.2)})
         
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
                self._camera.start_encoder(self._encoder,self._output,pts =VIDEO_ROOT_PATH+self._base_name +'_' + '{:04.0f}'.format(i) + '.txt')
                # à noter la sauvegarde du timestamp de la caméra
                
                '''
                #sauvegarde metadata cam
                self._dict_metadata=self._camera.capture_metadata()
                with open(VIDEO_ROOT_PATH+self._base_name +'_' + '{:04.0f}'.format(i) + '2.csv', 'w') as f:
                    w = csv.writer(f)
                    for row in self._dict_metadata.items():
                        w.writerow(row)
                '''
                
                #Création d'un CSV vidéo
                logging.debug("Fichier metadata caméra ouvert")
                self._csvv_file = open(VIDEO_ROOT_PATH+self._base_name +'_' + '{:04.0f}'.format(i) + '.csv', 'w')
                ligne = "Tps (s) ; TimeStamp ; ExpTime (µs) ; AnGain ; DiGain ; FrameDur (µs) ; Lux ; RedGains ; BlueGains"
                self._csvv_file.write(ligne + '\n')
                self._csvv_file.flush()
            
                paas=1. # pas de la boucle while qui vérifie si le bouton stop a été activé ou que le temps de séquence n'est pas dépassé
                time_debut=time.time()
                delta_time=0 #initialisation pour durée de la séquence
                j = 0 # initialisation pour ajustement Maison AWB
                k = 0 # initialisation pour 
                while self._boucle == True and delta_time < self._record_time:
                    delta_time = time.time()-time_debut
                    
                    if k % 5 == 0: # écriture métadata tous les 5*paas
                        mtd = Metadata(self._camera.capture_metadata())
                        ligne = f'{delta_time:.3f} ; {mtd.SensorTimestamp} ; {mtd.ExposureTime} ; {mtd.AnalogueGain:.2f} ; {mtd.DigitalGain:.2f} ; {mtd.FrameDuration} ; {mtd.Lux:.2f} ; {mtd.ColourGains[0]:.3f}; {mtd.ColourGains[1]:.3f}'
                        self._csvv_file.write(ligne + '\n')
                        self._csvv_file.flush()
                    
                    k = k+1
                    
                    if self._AWB == 2: #Ajustement Maison des gains AWB 
                        j=j+1
                        if j == int(15/paas): # 60 * 0.25 = 15 s entre les ajustements
                            self.adjust_histo(1,1,0.2) # on vise des ratios unitaires avec une tolérance de +- 20%
                            j = 0
                        else :
                            time.sleep(paas)
                    else: # Ajustement auto ou fixé, càd self._AWB = 0 ou 1               
                        time.sleep(paas)
                                        
                self._csvv_file.close()
                logging.debug("Fichier metadata caméra fermé")
                
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
    
    def RatiosRBsurG(self):
        """Capture puis calcul des ratios R/G et B/G"""        
        img = self._camera.capture_image("main")
        r,g,b,a = img.split()
        xx=np.linspace(0,255,256)
        r_med= sum(r.histogram()*xx)/sum(r.histogram())
        g_med= sum(g.histogram()*xx)/sum(g.histogram())
        b_med= sum(b.histogram()*xx)/sum(b.histogram())    
        return r_med/g_med,b_med/g_med
       
    def adjust_histo(self,rh,bh,tolerance):
        # Capture des gains AWB
        ColourGains = self._camera.capture_metadata()['ColourGains']       
        red=ColourGains[0]
        blue=ColourGains[1]               
        # Calcul des ratios R/G B/G
        ratioR,ratioB = self.RatiosRBsurG()
        # Paramètres de l'algo d'ajustement
        coef_convergence=0.9 # step de l'ajustement des gains awb
        i=0 # compteur initialisé pour sortir de la boucle si trop long
        imax=10 # nombre d'itérations max avant retour à référence
        while i<imax and (ratioR > rh+tolerance or ratioR < rh-tolerance or ratioB > bh+tolerance or ratioB < bh-tolerance) :
            red = red + coef_convergence*(rh-ratioR)
            blue = blue + coef_convergence*(bh-ratioB)
            # On threshold pour rester dans les clous 0&8
            a=min(7.88,red)
            red=max(0.5,a)
            b=min(7.8,blue)
            blue=max(0.5,b)
            #MàJ
            self._camera.set_controls({'ColourGains': (red, blue)})
            time.sleep(5*1/self._FRAMERATE) # 5 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            ratioR,ratioB = self.RatiosRBsurG()
            i=i+1
        else:
            if i < imax:
                logging.info('Coefficients AWB trouvés pour histogramme ajusté')
            else:
                logging.info('Coefficients AWB non trouvés, retour en mode awb_auto')
                self._camera.controls.AwbMode=0
                time.sleep(0.5)
                self._camera.set_controls({'AwbEnable': False})
              
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
    
