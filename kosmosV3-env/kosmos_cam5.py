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

#import GPS & capteur TP
from GPS import *
import ms5837


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
        self._X_RESOLUTION = aConf.get_val_int("31_PICAM_resolution_x",TERRAIN_SECTION)
        self._Y_RESOLUTION = aConf.get_val_int("32_PICAM_resolution_y",TERRAIN_SECTION)
        
        # Framerate et frameduration camera
        self._FRAMERATE=aConf.get_val_int("34_PICAM_framerate",TERRAIN_SECTION)
        self._FRAMEDURATION = int(1/self._FRAMERATE*1000000)
        
        # Temps de l'échantillonnage temporel des infos caméra. égal à celui le CSV TPGPS
        self._time_step = aConf.get_val_int("20_CSV_step_time",TERRAIN_SECTION)
        
        # Preview ou non
        self._PREVIEW = aConf.get_val_int("33_PICAM_preview",TERRAIN_SECTION)
        
        # si 1 : conversion mp4
        self._CONVERSION = aConf.get_val_int("36_PICAM_conversion_mp4",TERRAIN_SECTION)
        
        # A clarifier
        self._AWB = aConf.get_val_int("37_PICAM_AWB",TERRAIN_SECTION)
        self._record_time = aConf.get_val_int("35_PICAM_record_time",TERRAIN_SECTION)

        # Booléens pour les évènements
        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation Camera
        self._camera=Picamera2()
        self._video_config=self._camera.create_video_configuration()
        self._video_config['main']['size']=(self._X_RESOLUTION,self._Y_RESOLUTION)
        self._video_config['controls']['FrameDurationLimits']=(self._FRAMEDURATION,self._FRAMEDURATION)
        self._camera.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé

        self._camera.configure(self._video_config)
        self._camera.start() #A noter que le Preview.NULL démarre également 
        logging.info("Caméra démarrée")
        
        # Instanciation Encoder
        self._encoder=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)
             
        # Appel heure pour affichage sur la frame
        if aConf.get_val_int("38_PICAM_timestamp",TERRAIN_SECTION) == 1:
            self._camera.pre_callback = self.apply_timestamp
        
        #Initialisation GPS
        self._gps_ok = False
        try:
            self.gps = GPS()
            self.gps.start()  
            logging.info("Capteur GPS OK")
            self._gps_ok = True
        except:
            logging.error("Erreur d'initialisation du GPS")
            
        # Initialisation Capteur TP
        self._press_sensor_ok = False
        try:
            self.pressure_sensor = ms5837.MS5837_30BA()
            if self.pressure_sensor.init():
                self._press_sensor_ok = True
            logging.info("Capteur de pression OK")
        except:
            logging.error("Erreur d'initialisation du capteur de pression")
    
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
      
    def convert_to_mp4(self, input_file):
        if self._CONVERSION == 1:
            #Conversion h264 vers mp4 puis effacement du .h264
            output_file = os.path.splitext(input_file)[0] + '.mp4'              
            try:
                subprocess.run(['sudo', 'ffmpeg', '-probesize','2G','-r', str(self._FRAMERATE), '-i', input_file, '-c', 'copy', output_file, '-loglevel', 'warning'])
                logging.info("Conversion successful !")
                os.remove(input_file)
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
         
    def run(self):       
        while not self._end:
            i=0            
            while self._boucle == True:
                self._file_name = '{:02.0f}'.format(i) 
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                
                self._output = self._file_name + '_Video.h264'
                
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #éteint le Preview.NULL
                    self._camera.start_preview(Preview.QTGL,width=800,height=600)
                
                # Bloc d'enregistrement/encodage à proprement parler
                event_line = self._Conf.get_date_HMS()  + ";START ENCODER;" + self._output
                self._Conf.add_line("Events.csv",event_line)
                self._camera.start_encoder(self._encoder,self._output,pts = self._file_name+'_TimeStamp.txt')
                
                #Création CSV
                ligne = "HMS;Lat;Long;Pression;TempC;Delta(s);TStamp;ExpTime;AnG;DiG;Lux;RedG;BlueG;Bright"
                self._Conf.add_line(self._file_name + '_CamParam.csv',ligne)
                paas=1. # pas de la boucle while qui vérifie si le bouton stop a été activé ou que le temps de séquence n'est pas dépassé
                k_sampling = int(self._time_step / paas)
                intervalle_awb = 10 # en sec
                time_debut=time.time()
                delta_time=0 #initialisation pour durée de la séquence
                j = 0 # initialisation pour ajustement Maison AWB
                k = 0 # initialisation pour 
                while self._boucle == True and delta_time < self._record_time:
                    delta_time = time.time()-time_debut    
                    if k % k_sampling == 0: # écriture métadata tous les 5*paas
                        # Récupération données GPS
                        LAT = ""
                        LONG = ""
                        if self._gps_ok:
                            LAT = f'{self.gps.get_latitude():.5f}'
                            LONG = f'{self.gps.get_longitude():.5f}' 
                        #Récupération données TP
                        pressStr = ""
                        tempStr = ""
                        #profStr = ""
                        if self._press_sensor_ok:
                            if self.pressure_sensor.read():
                                press = self.pressure_sensor.pressure()  # Default is mbar (no arguments)
                                pressStr = f'{press:.1f}'
                                temp = self.pressure_sensor.temperature()  # Default is degrees C (no arguments)
                                tempStr = f'{temp:.1f}'
                                #prof=(press-1013)/100
                                #profStr=f'{prof:2f}'
                        # Récupération metadata caméra
                        mtd = Metadata(self._camera.capture_metadata())
                        bright = self._camera.camera_controls['Brightness'][2]
                        brightStr = f'{bright:.1f}'
                        # Ecriture des données dans le CSV
                        ligne = f'{self._Conf.get_date_HMS()};{LAT};{LONG};{pressStr};{tempStr};{delta_time:.1f};{mtd.SensorTimestamp};{mtd.ExposureTime};{mtd.AnalogueGain:.1f};{mtd.DigitalGain:.1f};{mtd.Lux:.1f};{mtd.ColourGains[0]:.1f};{mtd.ColourGains[1]:.1f};{brightStr}'
                        self._Conf.add_line(self._file_name + '_CamParam.csv',ligne)   
                    k = k+1
                    if self._AWB == 2: #Ajustement Maison des gains AWB 
                        j=j+1
                        if j == int(intervalle_awb/paas): 
                            self.adjust_awb(1,1,0.2) # on vise des ratios unitaires avec une tolérance de +- 20%
                            #time.sleep(0.5)
                            #self.adjust_brightness(120,20)
                            j = 0
                        else :
                            time.sleep(paas)
                    else: # Ajustement auto ou fixé, càd self._AWB = 0 ou 1               
                        time.sleep(paas)
                                        
                
                # Fin de l'encodage
                self._camera.stop_encoder()
                event_line = self._Conf.get_date_HMS() + ";END ENCODER;" + self._output
                self._Conf.add_line("Events.csv",event_line)
                               
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #stop .QTGL
                    self._camera.start_preview(Preview.NULL) #redemarrage .NULL
                    
                logging.info(f"Fin de l'enregistrement video {self._file_name}")
                
                # Conversion mp4 si demandée
                event_line =  self._Conf.get_date_HMS()  + ";START CONVERSION;" + self._output
                self._Conf.add_line("Events.csv",event_line)
                self.convert_to_mp4(self._output)
                event_line =  self._Conf.get_date_HMS()  + ";END CONVERSION;" + self._file_name +'_Video.mp4'
                self._Conf.add_line("Events.csv",event_line)
                
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
        #print(r_med,g_med,b_med)
        return r_med/g_med,b_med/g_med,(r_med+g_med+b_med)/3
       
    def adjust_awb(self,rh,bh,tolerance):
        event_line =  self._Conf.get_date_HMS()  + ";START AWB ALGO; "
        self._Conf.add_line("Events.csv",event_line)
        
        # Capture des gains AWB
        ColourGains = self._camera.capture_metadata()['ColourGains']
        red=ColourGains[0]
        blue=ColourGains[1]               
        # Calcul des ratios R/G B/G
        ratioR,ratioB = self.RatiosRBsurG()[0:2]
        # Paramètres de l'algo d'ajustement
        coef_convergence=0.8 # step de l'ajustement des gains awb
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
            time.sleep(10*self._FRAMEDURATION*0.000001) # 10 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            ratioR,ratioB = self.RatiosRBsurG()[0:2]
            i=i+1
        else:
            if i < imax:
                logging.info('Coefficients AWB trouvés')
            else:
                logging.info('Coefficients AWB non trouvés, retour en mode awb_auto')
                self._camera.controls.AwbMode=0
                time.sleep(0.5) 
                self._camera.set_controls({'AwbEnable': False})
                
        event_line =  self._Conf.get_date_HMS()  + ";END AWB ALGO; "
        self._Conf.add_line("Events.csv",event_line)
    
    def adjust_brightness(self,br,tolerance):
        event_line =  self._Conf.get_date_HMS()  + ";START BRIGHT ALGO; "
        self._Conf.add_line("Events.csv",event_line)
        
        # Capture de la brigthness
        brightness = self._camera.camera_controls['Brightness'][2]               
        # Calcul des ratios R/G B/G
        histo_med = self.RatiosRBsurG()[2]
        # Paramètres de l'algo d'ajustement
        coef_convergence=0.002 # step de l'ajustement de la brightness
        i=0 # compteur initialisé pour sortir de la boucle si trop long
        imax=10 # nombre d'itérations max avant retour à référence
        while i<imax and ( histo_med > br+tolerance or histo_med < br-tolerance ) :
            brightness = brightness + coef_convergence*(br-histo_med)
            # On threshold pour rester dans les clous 0&8
            a=min(0.99,brightness)
            brightness=max(-0.99,a)
            #MàJ
            self._camera.set_controls({'Brightness': brightness})                      
            time.sleep(10*self._FRAMEDURATION*0.000001) # 10 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            histo_med = self.RatiosRBsurG()[2]
            #print(histo_med)
            i=i+1
        else:
            if i < imax:
                logging.info('Coefficient Brightness trouvé')
            else:
                logging.info('Coefficient Brightness non trouvé, retour à la normale')
                self._camera.set_controls({'Brightness': 0})
                
                
        event_line =  self._Conf.get_date_HMS()  + ";END BRIGHT ALGO; "
        self._Conf.add_line("Events.csv",event_line) 
        
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle = False
        if self._gps_ok == True:
            self.gps.stop_thread()
        
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
    
