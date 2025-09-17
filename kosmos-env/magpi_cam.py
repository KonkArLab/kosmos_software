#!/usr/bin/python
# coding: utf-8
""" Camera MAGPI
 D. Hanon 21 novembre 2020 """

from threading import Thread, Event
import queue
import subprocess
import logging
from picamera2 import Picamera2,Preview,MappedArray,Metadata
import cv2
import hashlib
from collections import defaultdict
import concurrent.futures

import os
from kosmos_config import *
from PIL import Image
import numpy as np
import time
import csv
import json
from datetime import datetime

class ImageSaver(Thread):
    """
    Classe dérivée de Thread qui gère la sauvegarde d'images
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.queue = queue.Queue(maxsize=20)
        self.running = True
        
    def add_image(self, image_array, filename, quality, timestamp_flag):
        # Ajoute une image à la queue de sauvegarde
        try:
            self.queue.put((image_array, filename, quality, timestamp_flag), block=False)
            return True
        except:
            logging.warning("Queue de sauvegarde pleine, perte de fps")
            return False
    
    def run(self):
        while self.running or not self.queue.empty():
            try:
                image_data = self.queue.get(timeout=1.0)
                if image_data is None:
                    break
                
                image_array, filename, quality, timestamp_flag = image_data
                
                if timestamp_flag:
                    image_array = self.apply_timestamp(image_array)
                    
                image = Image.fromarray(image_array)
                
                image.save(filename, "JPEG", quality=quality)
                
                self.queue.task_done()
            
            except Exception as e:
                if self.running:
                    pass
        logging.debug("Thread Sauvegarde terminé")
                    
    def apply_timestamp(self, image_array):
        """
        Applique un timestamp sur l'image passée en paramètre
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        colour = (255, 255, 255)
        origin = (30, image_array.shape[0] - 50)
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1
        thickness = 2
        cv2.putText(image_array, timestamp, origin, font, scale, colour, thickness)
        return image_array
    
    def stop(self):
        self.running = False
        self.queue.put(None)

class MagpiCam(Thread):
    """
    Classe dérivée de Thread qui gère la capture d'images.
    """
    def __init__(self, aConf: KosmosConfig):
        """ constructeur de la classe ... initialise les paramètres
            Parameters:
                Conf (KosmosConfig) : gestionaire de la config
                aDate date : utilistée juste pour fixer le nom du fichier vidéo
        Dans le fichier de configuration :
             34_PICAM_framerate  : framerate
             33_PICAM_preview : si 1 : Lance la fenêtre de preview (utile en debug)
             35_PICAM_record_time : le temps d'enregistrement en secondes.
             37_PICAM_AWB : Règle l'ajustement de paramètres awb pour controle couleur : 0 picam classique, 1 awb fixé, 2 awb ajusté
             38_PICAM_timestamp : présence d'une incrustation avec le temps en haut à gauche
        """
        # On restreint les messages d'erreurs de PiCamera2 
        os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
        
        # Dénombrement des caméras disponibles
        self._CAM1_SENSOR = Picamera2.global_camera_info()[0]['Model'] 
        
        self._TIMESTAMP = False
        if aConf.config.getint(CONFIG_SECTION,"38_PICAM_timestamp") == 1:
            self._TIMESTAMP = True
        
        Thread.__init__(self)
        self._Conf = aConf
        if self._CAM1_SENSOR == 'imx296':
            self._X_RESOLUTION = 1456
            self._Y_RESOLUTION = 1088
        elif self._CAM1_SENSOR == 'imx477':
            self._X_RESOLUTION = 2028
            self._Y_RESOLUTION = 1080 # 1520
        elif self._CAM1_SENSOR == 'ov5647':
            self._X_RESOLUTION = 2592 # 2592
            self._Y_RESOLUTION = 1944 # 1944
        
        # Intervalle de capture correspondant au framerate
        self._CAPTURE_INTERVAL = 1.0/aConf.config.getint(DEBUG_SECTION,"34_PICAM_framerate")
        logging.debug(f"CAPTURE INTERVAL : {self._CAPTURE_INTERVAL}")
        
        self._IMAGE_FORMAT = "jpg" # Format de base mais png et autres disponibles
        self._IMAGE_QUALITY = 95 # Qualité maximale

        # Temps de l'échantillonnage temporel des infos caméra. égal à celui le CSV TPGPS
        self._time_step = aConf.config.getint(DEBUG_SECTION,"20_CSV_step_time")
        
        # Preview ou non
        self._PREVIEW = aConf.config.getint(DEBUG_SECTION,"33_PICAM_preview")
        
        # A clarifier
        self._AWB = aConf.config.getint(DEBUG_SECTION,"37_PICAM_AWB")
        self._record_time = np.inf#aConf.config.getint(CONFIG_SECTION,"02_TPS_ENREGISTREMENT")

        # Booléens pour les évènements
        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation objet Camera
        self._camera = Picamera2(0)
        self._still_config = self._camera.create_still_configuration()
        self._still_config['main']['size'] = (self._X_RESOLUTION,self._Y_RESOLUTION)
        self._camera.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé
        self._camera.configure(self._still_config)
        self._camera.start()      
            
        # Initialisation du thread de sauvegarde d'images
        self.image_saver = ImageSaver()
        self.image_saver.start()
        
        self._metadata_buffer = {}
    
    def capture_image2(self, camera, filename):
        """
        Capture une image avec la camera spécifiée
        """
        try:
            image_array = camera.capture_array("main")
            
            success = self.image_saver.add_image(
                                            image_array.copy(),
                                            filename,
                                            self._IMAGE_QUALITY,
                                            self._TIMESTAMP)
            return success
        
        except Exception as e:
            logging.error(f"Erreur lors de la capture d'image {filename}: {e}")
            return False
    
    def initialisation_awb(self):
        logging.info('Gains AWB ajustés par Algo Maison')
        self.adjust_awb(1,1,0.2)
    
    def RatiosRBsurG(self):
        """Capture puis calcul des ratios R/G et B/G"""        
        img = self._camera.capture_image("main")
        r,g,b = img.split()
        xx=np.linspace(0,255,256)
        r_med= sum(r.histogram()*xx)/sum(r.histogram())
        g_med= sum(g.histogram()*xx)/sum(g.histogram())
        b_med= sum(b.histogram()*xx)/sum(b.histogram())
        #print(r_med,g_med,b_med)
        return r_med/g_med,b_med/g_med,(r_med+g_med+b_med)/3
       
    def adjust_awb(self,rh,bh,tolerance):
        # Capture des gains AWB sur la caméra principale seulement
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
            
            time.sleep(0.4) # 10 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            ratioR,ratioB = self.RatiosRBsurG()[0:2]
            i=i+1
        else:
            if i < imax:
                logging.debug('Coefficients AWB trouvés')
            else:
                logging.error('Coefficients AWB non trouvés, retour en mode awb_auto')
                self._camera.controls.AwbMode=0
                time.sleep(0.5) 
                self._camera.set_controls({'AwbEnable': False})
    
    def run(self):       
        while not self._end:
            i=0            
            while self._boucle == True:
                # Création des codes stations
                increment = self._Conf.system.getint(INCREMENT_SECTION,"increment") 
                if i == 0:
                    self._session_name = f'{increment:04}'
                else:
                    self._session_name = f'{increment:04}' + '_' + '{:02.0f}'.format(i) 
                logging.info(f"Debut de la session de capture d'images {self._session_name}")
                
                session_folder = self._session_name
                if not os.path.exists(session_folder):
                    os.makedirs(session_folder)

                # Affichage du preview
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #éteint le Preview.NULL
                    X_preview = int(self._X_RESOLUTION/2)
                    Y_preview = int(self._X_RESOLUTION/2)
                    self._camera.start_preview(Preview.QTGL,x=100,y=300,width=X_preview,height=Y_preview)
                
                # Bloc d'enregistrement/encodage à proprement parler
                event_line = self._Conf.get_date_HMS()  + ";START IMAGE CAPTURE;" + self._session_name
                self._Conf.add_line(EVENT_FILE,event_line)
                
                #Insertion de la ligne d'en-tête du CSV
                ligne = "HMS;Delta(s);TStamp;ExpTime;AnG;DiG;Lux;RedG;BlueG;Bright"
                self._Conf.add_line(self._session_name + '.csv',ligne)

                time_debut = time.time()
                image_counter = 0
                next_capture_time = time_debut
                
                while self._boucle == True and (time.time() - time_debut) < self._record_time:
                    current_time = time.time()
                    
                    if current_time >= next_capture_time:
                        image_filename = os.path.join(self._session_name, f"{self._session_name}_{image_counter:06d}.{self._IMAGE_FORMAT}")
                        
                        self.capture_image2(self._camera, image_filename)

                        # Récupération des metadonnées caméra
                        mtd = Metadata(self._camera.capture_metadata())
                        delta_time = current_time - time_debut
                        bright = self._camera.camera_controls['Brightness'][2]
                        brightStr = f'{bright:.1f}'
                        ligne = f'{self._Conf.get_date_HMS()};{delta_time:.1f};{mtd.SensorTimestamp};{mtd.ExposureTime};{mtd.AnalogueGain:.1f};{mtd.DigitalGain:.1f};{mtd.Lux:.1f};{mtd.ColourGains[0]:.1f};{mtd.ColourGains[1]:.1f};{brightStr}'
                        self._Conf.add_line(self._session_name + '.csv',ligne)   
                        
                        image_counter += 1
                        next_capture_time += self._CAPTURE_INTERVAL
                        
                    sleep_time = next_capture_time - time.time()
                    if sleep_time > 0:
                        time.sleep(min(sleep_time, 0.001))
                
                event_line = self._Conf.get_date_HMS() + ";END IMAGE CAPTURE;" + self._session_name
                self._Conf.add_line(EVENT_FILE,event_line)
                
                # Ecriture json
                self.writeJSON(self._session_name)
                
                
                if self._PREVIEW == 1:
                    self._camera.stop_preview()
                    self._camera.start_preview(Preview.NULL)
                    
                logging.info(f"Fin de la session de capture {self._session_name}")
                
                i += 1
            self._start_again.wait()
            self._start_again.clear()            
        logging.info('Thread Camera terminé')
    
    def writeJSON(self,cam_file):
        # Creation du json contenant les infostations
        with open(GIT_PATH+'infoStationTemplate.json') as f:
            
            infoStationDict = json.load(f)
            infoStationDict["system"]["system"] = self._Conf.systemName
            infoStationDict["system"]["version"] = self._Conf.systemVersion
            infoStationDict["system"]["model"]=self._Conf.get_RPi_model()
            infoStationDict["system"]["camera"] = self._CAM1_SENSOR
            
            infoStationDict["video"]["stationDict"]["increment"] = f'{self._Conf.system.getint(INCREMENT_SECTION,"increment")-1:04}'
            
            # On sauvegarde date et heure venant de l'OS, même si on conservera aussi date et heure provenant du smartphone
            infoStationDict["video"]["hourDict"]["ymdOS"] = self._Conf.get_date_d()+"/"+self._Conf.get_date_m()+"/"+self._Conf.get_date_Y()
            infoStationDict["video"]["hourDict"]["HMSOS"] = self._Conf.get_date_H()+":"+self._Conf.get_date_M()+":"+self._Conf.get_date_S()
            
            '''
            # From sensors
            try:
                infoStationDict["video"]["gpsDict"]["latitude"] = float(self.gps.get_latitude())
                infoStationDict["video"]["gpsDict"]["longitude"] = float(self.gps.get_longitude())
            except:
                infoStationDict["video"]["gpsDict"]["latitude"] = None
                infoStationDict["video"]["gpsDict"]["longitude"] = None
                
            infoStationDict["video"]["ctdDict"]["salinity"] = None

            try:
                ma = self.PT()
                depth = (ma[0]-ma[1])/(1029*9.80665)
                infoStationDict["video"]["ctdDict"]["depth"] = depth
                infoStationDict["video"]["ctdDict"]["temperature"] = ma[2]
                infoStationDict["video"]["meteoAirDict"]["atmPress"] = ma[1]
                infoStationDict["video"]["meteoAirDict"]["tempAir"] = ma[3]
                #print(depth, ma[2],ma[1],ma[3])
            except:
                infoStationDict["video"]["ctdDict"]["depth"] = None
                infoStationDict["video"]["ctdDict"]["temperature"] = None
                infoStationDict["video"]["meteoAirDict"]["atmPress"] = None
                infoStationDict["video"]["meteoAirDict"]["tempAir"] = None
            '''
            
            with open(cam_file + '.json',mode = 'w', encoding = "utf-8") as ff:
                ff.write(json.dumps(infoStationDict, indent = 4))
    
    def stopCam(self):
        """
        Demande la fin de l'enregistrement et ferme l'objet caméra.
        """
        self._boucle = False
              
    def closeCam(self):
        """
        Arrêt des threads
        """
        self.image_saver.stop()
        self.image_saver.join()
            
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.stop()
        self._camera.close()
            
    def restart(self):
        """démarre ou redémarre le thread"""
        self._boucle=True
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()