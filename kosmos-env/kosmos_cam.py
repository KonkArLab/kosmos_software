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
import hashlib
from collections import defaultdict
from gpiozero import CPUTemperature


import os
from kosmos_config import *
from PIL import Image
import numpy as np
import time
import csv
import json

#import GPS capteur TP, LUX, magneto et hydrophone
from GPS import *
import ms5837
import kosmos_hydrophone as KHydro
import isl29125
import bmm150


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
             34_PICAM_framerate  : framerate
             33_PICAM_preview : si 1 : Lance la fenêtre de preview (utile en debug)
             35_PICAM_record_time : le temps d'enregistrement en secondes.
             36_PICAM_conversion_mp4 : 1 si on souhaite effectuer la conversion juste après l'acquisition
             37_PICAM_AWB : Règle l'ajustemetn de paramètres awb pour controle couleur : 0 picam classique, 1 awb fixé, 2 awb ajusté
             38_PICAM_timestamp : présence d'une incrustation avec le temps en haut à gauche
             39_PICAM_stereo : 1 si on souhaite capturer en stéréo, 0 sinon. A noter que si c'est à 1 alors qu'il n'y a qu'une caméra, le soft ne s'arrêtera pas. 
        """
        # On restreint les messages d'erreurs de PiCamera2 
        os.environ["LIBCAMERA_LOG_LEVELS"] = "3"
        
        # Dénombrement des caméras disponibles
        self._CAM_NUMBER = len(Picamera2.global_camera_info())
        self._CAM1_SENSOR = Picamera2.global_camera_info()[0]['Model']
        if self._CAM_NUMBER == 2:
            self._CAM2_SENSOR = Picamera2.global_camera_info()[1]['Model']
            if self._CAM1_SENSOR == self._CAM2_SENSOR:
                if aConf.config.getint(CONFIG_SECTION,"08_STEREO") == 1:
                    logging.info(f"Deux caméras indentiques détectées {self._CAM1_SENSOR}-> MODE STEREO")
                    self.STEREO = True
                else:
                    logging.info(f"Deux caméras indentiques détectées mais MODE MONO demandé")
                    self.STEREO = False
            else:
                logging.error(f"Deux caméras détectées mais différentes -> MODE MONO")
                self.STEREO = False
        else:
            logging.info(f"Une caméra détectée {self._CAM1_SENSOR} -> MODE MONO")
            self.STEREO = False   
        
        Thread.__init__(self)
        self._Conf = aConf    
        # Résolutions horizontale
        if self._CAM1_SENSOR == 'imx296':
            self._X_RESOLUTION = 1456
            self._Y_RESOLUTION = 1088
            #tuning = Picamera2.load_tuning_file(GIT_PATH+"imx296_kosmos.json")
            #algo = Picamera2.find_tuning_algo(tuning,"rpi.awb")
            #algo["sensitivity_r"] = 1.05
        elif self._CAM1_SENSOR == 'imx477':
            self._X_RESOLUTION = 2028
            self._Y_RESOLUTION = 1080#1520
            #tuning = Picamera2.load_tuning_file("imx477.json")          
        elif self._CAM1_SENSOR == 'ov5647':
            self._X_RESOLUTION = 1920
            self._Y_RESOLUTION = 1080
         
        # Framerate et frameduration camera
        self._FRAMERATE=aConf.config.getint(DEBUG_SECTION,"34_PICAM_framerate")
        self._FRAMEDURATION = int(1/self._FRAMERATE*1000000)
        
        # Temps de l'échantillonnage temporel des infos caméra. égal à celui le CSV TPGPS
        self._time_step = aConf.config.getint(DEBUG_SECTION,"20_CSV_step_time")
        
        # Preview ou non
        self._PREVIEW = aConf.config.getint(DEBUG_SECTION,"33_PICAM_preview")
        
        # si 1 : conversion mp4
        self._CONVERSION = aConf.config.getint(DEBUG_SECTION,"36_PICAM_conversion_mp4")
        
        # A clarifier
        self._AWB = aConf.config.getint(DEBUG_SECTION,"37_PICAM_AWB")
        self._record_time = aConf.config.getint(CONFIG_SECTION,"02_TPS_ENREGISTREMENT")

        # Booléens pour les évènements
        self._end = False
        self._boucle = True
        self._start_again = Event()
     
        # Instanciation Camera
        self._camera = Picamera2(0)#,tuning = tuning)
        self._video_config = self._camera.create_video_configuration()
        self._video_config['main']['size'] = (self._X_RESOLUTION,self._Y_RESOLUTION)
        self._video_config['controls']['FrameDurationLimits'] = (self._FRAMEDURATION,self._FRAMEDURATION)
        self._camera.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé
        self._camera.configure(self._video_config)
        self._camera.start() #A noter que le Preview.NULL démarre également 
        #logging.info("Caméra démarrée")      
        # Instanciation Encoder
        self._encoder=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)
        
        # Appel heure pour affichage sur la frame
        if aConf.config.getint(CONFIG_SECTION,"38_PICAM_timestamp") == 1:
            self._camera.pre_callback = self.apply_timestamp
        
        #Initialisation deuxième CAMéRA pour stéréo    
        if self.STEREO:      
            self._camera2 = Picamera2(1)
            self._camera2.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé
            self._camera2.configure(self._video_config) # même config pour les deux caméras            
            self._camera2.start() #A noter que le Preview.NULL démarre également 
            #logging.info("Caméra stéréo démarrée") 
            # Instanciation Encoder    
            self._encoder2=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)            
        
        # Initialisation Capteur TP        
        self._press_sensor_ok = False
        try:
            self.pressure_sensor = ms5837.MS5837_30BA()        
            if self.pressure_sensor.init():
                self._press_sensor_ok = True
            logging.info("Capteur de pression OK")
        except Exception as e:
            logging.error("Erreur d'initialisation du capteur de pression ")
        
        #Initialisation GPS
        self._gps_ok = False
        try:
            self.gps = GPS()
            if self.gps.init():
                logging.info("Capteur GPS OK")
                self._gps_ok = True
                self.gps.start()
            else:    
                logging.error("Port Serie GPS OK mais non fonctionnel")
        except:    
            logging.error("Erreur d'initialisation du GPS")
            
        # Initialisation Capteur lumière        
        self._light_sensor_ok = False
        try:
            self.light_sensor = isl29125.RGBSensor()
            if self.light_sensor.init():
                self._light_sensor_ok = True
                logging.info("Capteur de lumière OK")
            else:
                logging.error("Port série lumière OK mais non fonctionnel")
        except Exception as e:
            logging.error("Erreur d'initialisation du capteur de lumière")
            
        # Initialisation Capteur magneto        
        self._magneto_sensor_ok = False
        try:
            self.magneto_sensor = bmm150.magnetoSensor()
            if self.magneto_sensor.init():
                self._magneto_sensor_ok = True
                logging.info("Magnétomètre OK")
            else:
                logging.error("Port série magnétomètre OK mais non fonctionnel")
        except Exception as e:
            logging.error("Erreur d'initialisation du magnetomètre")
        
    
        # Definition Thread Hydrophone
        self.PRESENCE_HYDRO = self._Conf.config.getint(CONFIG_SECTION,"07_HYDROPHONE") # Fonctionnement hydrophone si 1
        if self.PRESENCE_HYDRO==1:
            self.thread_hydrophone = KHydro.KosmosHydro(self._Conf)
            logging.info("Hydrophone démarré")
        else:
            logging.info("Hydrophone non démarré")
                        
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
            wav_file = os.path.splitext(input_file)[0] + '.wav'
            output_file = os.path.splitext(input_file)[0] + '.mp4'
            
            try:
                if self.PRESENCE_HYDRO == 1 and self._Conf.get_RPi_model().split(' ')[2] == '4':
                    #subprocess.run(['sudo', 'ffmpeg', '-probesize','2G','-r', str(self._FRAMERATE), '-i', input_file, '-c', 'copy', output_file, '-loglevel', 'warning'])
                    # décommenter ci dessous sin on veut merger son vidéo
                    subprocess.run(['sudo', 'ffmpeg', '-probesize','2G','-r', str(self._FRAMERATE), '-i', input_file, '-i', wav_file, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', output_file, '-loglevel', 'warning'])
                else:
                    subprocess.run(['sudo', 'ffmpeg', '-probesize','2G','-r', str(self._FRAMERATE), '-i', input_file, '-c', 'copy', output_file, '-loglevel', 'warning'])
                logging.info("Conversion video 1 successful !")
                os.remove(input_file)
                logging.debug(f"Deleted input H.264 file: {input_file}")                
                # Ajouter la métadonnée personnalisée
                #custom_value = "KOSMOS_TEST"  # Test 
                #self.add_metadata(output_file, custom_value)
                
                if self.STEREO == 1:
                    input_file2 = os.path.splitext(input_file)[0]+'_STEREO.h264'
                    output_file2 = os.path.splitext(input_file)[0] +'_STEREO.mp4'
                    subprocess.run(['sudo', 'ffmpeg', '-probesize','2G','-r', str(self._FRAMERATE), '-i', input_file2, '-c', 'copy', output_file2, '-loglevel', 'warning'])
                    logging.info("Conversion video 2 successful !")
                    os.remove(input_file2)
                    logging.debug(f"Deleted input H.264 file: {input_file2}")
                    
            except subprocess.CalledProcessError as e:
                logging.error("Error during conversion:", e, " !!!")       
        else:
            logging.info("Pas de conversion mp4 demandée")
            
    def add_metadata(self, video_file, custom_value):
        """
        Ajoute une métadonnée personnalisée à une vidéo MP4 avec exiftool.
        """
        try:
            # Chemin complet vers le fichier de configuration exiftool
            config_path = os.path.abspath(WORK_PATH+'config/exiftool_config')
            hashed_value = self.hash_encoder(custom_value)
            command = ['exiftool', '-config', config_path, f'-kosmos={hashed_value}', '-overwrite_original', video_file]
            
            # Afficher la commande pour débogage
            logging.debug("Commande appelée :", " ".join(command))
            
            # Exécuter la commande
            subprocess.run(command, check=True)
            logging.info(f"Metadonnée '-kosmos={hashed_value}' ajoutée à {video_file}")

        except subprocess.CalledProcessError as e:
            logging.error(f"Erreur lors de l'ajout des métadonnées : {e}")


    def hash_encoder(self, p_text) :
        return hashlib.sha256(p_text.encode()).hexdigest()

    def initialisation_awb(self):
        if self._AWB == 0:
            logging.info('Gains AWB ajustés par Rpi')
            self._camera.set_controls({'AwbEnable': True})
            self._camera.controls.AwbMode=0
            if self.STEREO:
                self._camera2.set_controls({'AwbEnable': True})
                self._camera2.controls.AwbMode=0        
        else:
            if self._AWB == 1:
                logging.info('Gains AWB fixes')
                self._camera.controls.AwbMode=0
                time.sleep(0.5)
                self._camera.set_controls({'AwbEnable': False})
                if self.STEREO:
                    self._camera2.set_controls({'AwbEnable': False})
                    self._camera2.set_controls({'ColourGains': self._camera.capture_metadata()['ColourGains']})
            if self._AWB == 2:
                logging.info('Gains AWB ajustés par Algo Maison')
                self.adjust_awb(1,1,0.2)
            
    def run(self):       
        while not self._end:
            i=0            
            while self._boucle == True:
                # Création des codes stations
                increment = self._Conf.system.getint(INCREMENT_SECTION,"increment") 
                if i == 0: # Mode STAVIRO, une seule vidéo de longue durée
                    self._file_name = f'{increment:04}'
                else: # Mode MICADO, découpage de la vidéo en morceau de XX minutes
                    self._file_name = f'{increment:04}' + '_' + '{:02.0f}'.format(i) 
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                
                self._output = self._file_name + '.h264'
                if self.STEREO:
                    self._output2 = self._file_name + '_stereo' + '.h264'

                # Affichage du preview
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #éteint le Preview.NULL
                    X_preview = int(self._X_RESOLUTION/2)
                    Y_preview = int(self._X_RESOLUTION/2)
                    self._camera.start_preview(Preview.QTGL,x=100,y=300,width=X_preview,height=Y_preview)
                    if self.STEREO:
                        self._camera2.stop_preview() #éteint le Preview.NULL
                        self._camera2.start_preview(Preview.QTGL, x=100+X_preview,y=300,width=X_preview,height=Y_preview)    
                
                # Bloc d'enregistrement/encodage à proprement parler
                event_line = self._Conf.get_date_HMS()  + ";START ENCODER;" + self._output
                self._Conf.add_line(EVENT_FILE,event_line)
                self._camera.start_encoder(self._encoder,self._output,pts = self._file_name+'.txt')
                if self.STEREO:
                    self._camera2.start_encoder(self._encoder2,self._output2,pts = self._file_name+'_stereo.txt')
                
                if self.PRESENCE_HYDRO == 1:
                    self.thread_hydrophone.restart()
                
                #Création CSV
                ligne = "HMS;Lat;Long;Pression;TempC;RLux;GLux;BLux;XMagneto;YMagneto;ZMagneto;TempCPU;Delta(s);TStamp;ExpTime;AnG;DiG;Lux;RedG;BlueG;Bright"
                if self.STEREO:
                    ligne="HMS;Lat;Long;Pression;TempC;RLux;GLux;BLux;XMagneto;YMagneto;ZMagneto;TempCPU;Delta(s);TStamp;ExpTime;AnG;DiG;Lux;RedG;BlueG;Bright;TStamp2;ExpTime2;AnG2;DiG2;Lux2;RedG2;BlueG2;Bright2"
                self._Conf.add_line(self._file_name + '.csv',ligne)
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
                            try:
                                LAT = self.gps.get_latitude()
                                LONG = self.gps.get_longitude()
                            except:
                                logging.debug("Erreur de récupération des données GPS")
                        #Récupération données TP
                        pressStr = ""
                        tempStr = ""
                        if self._press_sensor_ok:
                            try:
                                if self.pressure_sensor.read():
                                    press = self.pressure_sensor.pressure()  # Default is mbar (no arguments)
                                    pressStr = f'{press:.1f}'
                                    temp = self.pressure_sensor.temperature()  # Default is degrees C (no arguments)
                                    tempStr = f'{temp:.1f}'
                            except:
                                logging.debug("Erreur de récupération des données TP")
                                
                        # Récupération lumière
                        lux_r = ""
                        lux_g = ""
                        lux_b = ""
                        if self._light_sensor_ok:
                            try:
                                r, g, b = self.light_sensor.read()
                                lux_r = f"{r}"
                                lux_g = f"{g}"
                                lux_b = f"{b}"
                            except:
                                logging.error("Erreur de récupération des données lumière")
                                
                        # Récupération magneto
                        magneto_x = ""
                        magneto_y = ""
                        magneto_z = ""
                        if self._magneto_sensor_ok:
                            try:
                                x,y,z = self.magneto_sensor.read()
                                magneto_x = f"{x:.2f}"
                                magneto_y = f"{y:.2f}"
                                magneto_z = f"{z:.2f}"
                            except:
                                logging.debug("Erreur de récupération des données magneto")
    
                        # Récupération température CPU
                        cpuStr = f'{CPUTemperature().temperature:.2f}'
                        
                        # Récupération metadata caméra
                        mtd = Metadata(self._camera.capture_metadata())
                        bright = self._camera.camera_controls['Brightness'][2]
                        brightStr = f'{bright:.1f}'
                        ligne = f'{self._Conf.get_date_HMS()};{LAT};{LONG};{pressStr};{tempStr};{lux_r};{lux_g};{lux_b};{magneto_x};{magneto_y};{magneto_z};{cpuStr};{delta_time:.1f};{mtd.SensorTimestamp};{mtd.ExposureTime};{mtd.AnalogueGain:.1f};{mtd.DigitalGain:.1f};{mtd.Lux:.1f};{mtd.ColourGains[0]:.1f};{mtd.ColourGains[1]:.1f};{brightStr}'
                        if self.STEREO:
                            mtd2 = Metadata(self._camera2.capture_metadata())
                            bright2 = self._camera2.camera_controls['Brightness'][2]
                            brightStr2 = f'{bright2:.1f}'
                            ligne = f'{self._Conf.get_date_HMS()};{LAT};{LONG};{pressStr};{tempStr};{lux_r};{lux_g};{lux_b};{magneto_x};{magneto_y};{magneto_z};{cpuStr};{delta_time:.1f};{mtd.SensorTimestamp};{mtd.ExposureTime};{mtd.AnalogueGain:.1f};{mtd.DigitalGain:.1f};{mtd.Lux:.1f};{mtd.ColourGains[0]:.1f};{mtd.ColourGains[1]:.1f};{brightStr};{mtd2.SensorTimestamp};{mtd2.ExposureTime};{mtd2.AnalogueGain:.1f};{mtd2.DigitalGain:.1f};{mtd2.Lux:.1f};{mtd2.ColourGains[0]:.1f};{mtd2.ColourGains[1]:.1f};{brightStr2}'
                        self._Conf.add_line(self._file_name + '.csv',ligne)   
                    k = k+1
                    if self._AWB == 2: #Ajustement Maison des gains AWB 
                        j=j+1
                        if j == int(intervalle_awb/paas):
                            event_line =  self._Conf.get_date_HMS()  + ";START AWB ALGO; "
                            self._Conf.add_line(EVENT_FILE,event_line)
                            self.adjust_awb(1,1,0.2) # on vise des ratios unitaires avec une tolérance de +- 20%
                            event_line =  self._Conf.get_date_HMS()  + ";END AWB ALGO; "
                            self._Conf.add_line(EVENT_FILE,event_line)       
                            j = 0
                        else :
                            time.sleep(paas)
                    else: # Ajustement auto ou fixé, càd self._AWB = 0 ou 1               
                        time.sleep(paas)
                                        
                # Fin de l'encodage
                self._camera.stop_encoder()
                if self.STEREO:
                    self._camera2.stop_encoder()
                if self.PRESENCE_HYDRO == 1:
                    self.thread_hydrophone.pause()
                    self.thread_hydrophone.save_audio(self._file_name + '.wav')
                
                
                event_line = self._Conf.get_date_HMS() + ";END ENCODER;" + self._output
                self._Conf.add_line(EVENT_FILE,event_line)
                               
                # Ecriture json
                self.writeJSON(self._file_name)
                ## Ajout d'une ligne dans le InfoStation.csv
                #self._Conf.addInfoStation(self._file_name+'.json')
                               
                if self._PREVIEW == 1:
                    self._camera.stop_preview() #stop .QTGL
                    self._camera.start_preview(Preview.NULL) #redemarrage .NULL
                    if self.STEREO:
                        self._camera2.stop_preview() #éteint le Preview.NULL
                        self._camera2.start_preview(Preview.NULL)
                    
                logging.info(f"Fin de l'enregistrement video {self._file_name}")
                
                # Conversion mp4 si demandée
                event_line =  self._Conf.get_date_HMS()  + ";START CONVERSION;" + self._output
                self._Conf.add_line(EVENT_FILE,event_line)
                self.convert_to_mp4(self._output)
                event_line =  self._Conf.get_date_HMS()  + ";END CONVERSION;" + self._file_name +'.mp4'
                self._Conf.add_line(EVENT_FILE,event_line)
                
                i=i+1
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
            
            
            with open(cam_file + '.json',mode = 'w', encoding = "utf-8") as ff:
                ff.write(json.dumps(infoStationDict, indent = 4))
    
    def PT(self):
        try:
            columns = defaultdict(list) # each value in each column is appended to a list
            with open(self._file_name +'.csv') as f:
                reader = csv.DictReader(f, delimiter=';') # read rows into a dictionary format
                for row in reader: # read a row as {column1: value1, column2: value2,...}
                    for (k,v) in row.items(): # go over each column name and value 
                        columns[k].append(v) # append the value into the appropriate list
                x = np.array(columns['Pression'], dtype=float)
                y = np.array(columns['TempC'], dtype=float)
                Pfond = np.max(x)
                Psurf = np.min(x)
                IndFond = np.argmax(x)
                IndSurf = np.argmin(x)
                Tfond = y[IndFond]
                Tsurf = y[IndSurf]
                ma = Pfond,Psurf,Tfond,Tsurf
        except:
            ma = None, None, None, None
        return ma 
    
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
            if self.STEREO:
                self._camera2.set_controls({'ColourGains': (red, blue)})
            time.sleep(10*self._FRAMEDURATION*0.000001) # 10 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            ratioR,ratioB = self.RatiosRBsurG()[0:2]
            i=i+1
        else:
            if i < imax:
                logging.debug('Coefficients AWB trouvés')
            else:
                logging.error('Coefficients AWB non trouvés, retour en mode awb_auto')
                self._camera.controls.AwbMode=0
                if self.STEREO:
                    self._camera2.controls.AwbMode=0
                time.sleep(0.5) 
                self._camera.set_controls({'AwbEnable': False})
                if self.STEREO:
                    self._camera2.set_controls({'AwbEnable': False})

    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle = False
              
    def closeCam(self):
        """Arrêt du GPS"""
        if self._gps_ok == True:    
            self.gps.stop_thread()
        """Arrêt du TP"""
        if self._press_sensor_ok == True:
            self.pressure_sensor._bus.close()
        
        #"""Arrêt hydrophone"""
        #if self.PRESENCE_HYDRO == 1:
        #    self.thread_hydrophone.stop_thread()   
        #    if self.thread_hydrophone.is_alive():
        #        self.thread_hydrophone.join() 
        
        
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.stop()    
        #logging.info("Caméra arrêtée")
        self._camera.close()
        #logging.info("Caméra éteinte")
        if self.STEREO:
            self._camera2.stop()    
            #logging.info("Caméra stéréo arrêtée")
            self._camera2.close()
            #logging.info("Caméra stéréo éteinte")
         
            
    def restart(self):
        """démarre ou redémarre le thread"""
        self._boucle=True
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()
    
