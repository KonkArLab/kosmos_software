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
import json

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
        self._X_RESOLUTION = aConf.config.getint(CONFIG_SECTION,"31_PICAM_resolution_x")
        self._Y_RESOLUTION = aConf.config.getint(CONFIG_SECTION,"32_PICAM_resolution_y")
        
        # Framerate et frameduration camera
        self._FRAMERATE=aConf.config.getint(CONFIG_SECTION,"34_PICAM_framerate")
        self._FRAMEDURATION = int(1/self._FRAMERATE*1000000)
        
        # Temps de l'échantillonnage temporel des infos caméra. égal à celui le CSV TPGPS
        self._time_step = aConf.config.getint(CONFIG_SECTION,"20_CSV_step_time")
        
        # Preview ou non
        self._PREVIEW = aConf.config.getint(CONFIG_SECTION,"33_PICAM_preview")
        
        # si 1 : conversion mp4
        self._CONVERSION = aConf.config.getint(CONFIG_SECTION,"36_PICAM_conversion_mp4")
        
        # A clarifier
        self._AWB = aConf.config.getint(CONFIG_SECTION,"37_PICAM_AWB")
        self._record_time = aConf.config.getint(CONFIG_SECTION,"35_PICAM_record_time")

        # Booléens pour les évènements
        self._end = False
        self._boucle = True
        self._start_again = Event()
        
        # Booléen pour la Stéréo
        if aConf.config.getint(CONFIG_SECTION,"39_PICAM_stereo") == 1:
            self.STEREO = True
            logging.info("Mode STEREO demandé")
        else:
            self.STEREO = False
     
        # Instanciation Camera
        self._camera = Picamera2(0)
        self._video_config = self._camera.create_video_configuration()
        self._video_config['main']['size'] = (self._X_RESOLUTION,self._Y_RESOLUTION)
        self._video_config['controls']['FrameDurationLimits'] = (self._FRAMEDURATION,self._FRAMEDURATION)
        self._camera.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé
        self._camera.configure(self._video_config)
        self._camera.start() #A noter que le Preview.NULL démarre également 
        logging.info("Caméra démarrée")
              
        # Instanciation Encoder
        self._encoder=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)
        
        if self.STEREO:
            self._camera2 = Picamera2(1)
            self._video_config2 = self._camera2.create_video_configuration()
            self._video_config2['main']['size'] = (self._X_RESOLUTION,self._Y_RESOLUTION)
            self._video_config2['controls']['FrameDurationLimits'] = (self._FRAMEDURATION,self._FRAMEDURATION)
            self._camera2.set_controls({'AeExposureMode': 'Short'}) # on privilégie une adaptation par gain analogique que par augmentation du tps d'expo, et ce, pour limiter le flou de bougé
            self._camera2.configure(self._video_config2)
            try:
                self._camera2.start() #A noter que le Preview.NULL démarre également 
                logging.info("Caméra stéréo démarrée")
            except:
                self.STEREO = False
                logging.error("Camera stéréo non détectée")
            self._encoder2=H264Encoder(framerate=self._FRAMERATE, bitrate=10000000)
            
        
        
        # Appel heure pour affichage sur la frame
        if aConf.config.getint(CONFIG_SECTION,"38_PICAM_timestamp") == 1:
            self._camera.pre_callback = self.apply_timestamp
        
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
            if self.STEREO:
                self._camera2.controls.AwbMode=0
        elif self._AWB == 1:
            logging.info('Gains AWB fixes')
            if self.STEREO:
                self._camera2.controls.AwbMode=0
            self._camera.controls.AwbMode=0
            time.sleep(0.5)
            self._camera.set_controls({'AwbEnable': False})
            if self.STEREO:
                self._camera2.set_controls({'AwbEnable': False})
        elif self._AWB == 2:
            logging.info('Gains AWB ajustés par Algo Maison')
            self._camera.controls.AwbMode=0
            if self.STEREO:
                self._camera2.controls.AwbMode=0
            time.sleep(0.5)
            self._camera.set_controls({'AwbEnable': False})
            if self.STEREO:
                self._camera2.set_controls({'AwbEnable': False})
         
    def run(self):       
        while not self._end:
            i=0            
            while self._boucle == True:
                increment = self._Conf.system.getint(INCREMENT_SECTION,"increment") 
                video_file = self._Conf.config.get(CAMPAGNE_SECTION,"zone") + f'{self._Conf.get_date_Y()}' + f'{increment:04}'
                if i == 0:
                    self._file_name = video_file
                else:
                    self._file_name = video_file + '_' + '{:02.0f}'.format(i)+'_' 
                logging.info(f"Debut de l'enregistrement video {self._file_name}")
                
                self._output = self._file_name + '.h264'
                if self.STEREO:
                    self._output2 = self._file_name + '_2' + '.h264'

                if self._PREVIEW == 1:
                    self._camera.stop_preview() #éteint le Preview.NULL
                    self._camera.start_preview(Preview.QTGL,x=100,y=300,width=400,height=300)
                    if self. STEREO:
                        self._camera2.stop_preview() #éteint le Preview.NULL
                        self._camera2.start_preview(Preview.QTGL, x=500,y=300,width=400,height=300)    
                
                # Bloc d'enregistrement/encodage à proprement parler
                event_line = self._Conf.get_date_HMS()  + ";START ENCODER;" + self._output
                self._Conf.add_line(EVENT_FILE,event_line)
                self._camera.start_encoder(self._encoder,self._output,pts = self._file_name+'.txt')
                if self.STEREO:
                    self._camera2.start_encoder(self._encoder2,self._output2,pts = self._file_name+'_2.txt')

                #Création CSV
                ligne = "HMS;Lat;Long;Pression;TempC;Delta(s);TStamp;ExpTime;AnG;DiG;Lux;RedG;BlueG;Bright"
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
                            LAT = self.gps.get_latitude()
                            LONG = self.gps.get_longitude() 
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
                        self._Conf.add_line(self._file_name + '.csv',ligne)   
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
                if self.STEREO:
                    self._camera2.stop_encoder()
                event_line = self._Conf.get_date_HMS() + ";END ENCODER;" + self._output
                self._Conf.add_line(EVENT_FILE,event_line)
                               
                # ecriture json
                self.writeJSON(self._file_name)
                self._Conf.addInfoStation(self._file_name+'.json')
                               
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
                self.convert_to_mp4(self._output2)
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
            infoStationDict["system"]["camera"] = "picam"
            infoStationDict["system"]["moteur"] = "brushless"
            infoStationDict["campagne"]["zoneDict"]["campagne"] = self._Conf.config.get(CAMPAGNE_SECTION,"campagne")
            infoStationDict["campagne"]["zoneDict"]["zone"] = self._Conf.config.get(CAMPAGNE_SECTION,"zone")
            infoStationDict["campagne"]["zoneDict"]["lieudit"] = self._Conf.config.get(CAMPAGNE_SECTION,"lieudit")
            infoStationDict["campagne"]["zoneDict"]["protection"] = self._Conf.config.get(CAMPAGNE_SECTION,"protection")
            infoStationDict["campagne"]["dateDict"]["year"] = self._Conf.get_date_Y()
            infoStationDict["campagne"]["dateDict"]["month"] = self._Conf.get_date_m()
            infoStationDict["campagne"]["dateDict"]["day"] = self._Conf.get_date_d()
            infoStationDict["campagne"]["dateDict"]["date"] = self._Conf.get_date_d()+"/"+self._Conf.get_date_m()+"/"+self._Conf.get_date_Y()
            infoStationDict["campagne"]["deploiementDict"]["bateau"] = self._Conf.config.get(CAMPAGNE_SECTION,"bateau")
            infoStationDict["campagne"]["deploiementDict"]["pilote"] = self._Conf.config.get(CAMPAGNE_SECTION,"pilote")
            infoStationDict["campagne"]["deploiementDict"]["equipage"] = self._Conf.config.get(CAMPAGNE_SECTION,"equipage")
            infoStationDict["campagne"]["deploiementDict"]["partenaires"] = self._Conf.config.get(CAMPAGNE_SECTION,"partenaires")
            infoStationDict["video"]["codeStation"] = self._Conf.config.get(CAMPAGNE_SECTION,"zone") + f'{self._Conf.get_date_Y()}' + f'{self._Conf.system.getint(INCREMENT_SECTION,"increment"):04}'
            # Pour hms, on va utiliser la clock de la Rpi et le temps sera pris à cet endroit dans la boucle, càd à la fin de l'enregistrement
            infoStationDict["video"]["heureDict"]["heure"] = self._Conf.get_date_H()
            infoStationDict["video"]["heureDict"]["minute"] = self._Conf.get_date_M()
            infoStationDict["video"]["heureDict"]["seconde"] = self._Conf.get_date_S()
            infoStationDict["video"]["gpsDict"]["site"] = ""
            infoStationDict["video"]["gpsDict"]["latitude"] = ""
            infoStationDict["video"]["gpsDict"]["longitude"] = ""
            infoStationDict["video"]["ctdDict"]["profondeur"] = ""
            infoStationDict["video"]["ctdDict"]["temperature"] = ""
            infoStationDict["video"]["ctdDict"]["salinite"] = ""
            infoStationDict["video"]["astroDict"]["lune"] = ""
            infoStationDict["video"]["astroDict"]["maree"] = ""
            infoStationDict["video"]["astroDict"]["coefficient"] = ""
            infoStationDict["video"]["meteoAirDict"]["ciel"] = ""
            infoStationDict["video"]["meteoAirDict"]["vent"] = ""
            infoStationDict["video"]["meteoAirDict"]["direction"] = ""
            infoStationDict["video"]["meteoAirDict"]["atmPress"] = ""
            infoStationDict["video"]["meteoAirDict"]["tempAir"] = ""
            infoStationDict["video"]["meteoMerDict"]["etatMer"] = ""
            infoStationDict["video"]["meteoMerDict"]["houle"] = ""
            infoStationDict["video"]["analyseDict"]["exploitabilite"] = ""
            infoStationDict["video"]["analyseDict"]["habitat"] = ""
            infoStationDict["video"]["analyseDict"]["faune"] = ""
            infoStationDict["video"]["analyseDict"]["visibilite"] = ""

            with open(cam_file + '.json',mode = 'w', encoding = "utf-8") as ff:
                json.dump(infoStationDict,ff)
    
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
        self._Conf.add_line(EVENT_FILE,event_line)
        
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
            if self.STEREO:
                self._camera2.set_controls({'ColourGains': (red, blue)})
            time.sleep(10*self._FRAMEDURATION*0.000001) # 10 frames de décalage entre modif des gain awb et calcul des nouveaux R/G etB/G
            ratioR,ratioB = self.RatiosRBsurG()[0:2]
            i=i+1
        else:
            if i < imax:
                logging.info('Coefficients AWB trouvés')
            else:
                logging.error('Coefficients AWB non trouvés, retour en mode awb_auto')
                self._camera.controls.AwbMode=0
                if self.STEREO:
                    self._camera2.controls.AwbMode=0
                time.sleep(0.5) 
                self._camera.set_controls({'AwbEnable': False})
                if self.STEREO:
                    self._camera2.set_controls({'AwbEnable': False})

        event_line =  self._Conf.get_date_HMS()  + ";END AWB ALGO; "
        self._Conf.add_line(EVENT_FILE,event_line)
    
    """
    def adjust_brightness(self,br,tolerance):
        event_line =  self._Conf.get_date_HMS()  + ";START BRIGHT ALGO; "
        self._Conf.add_line(EVENT_FILE,event_line)
        
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
        self._Conf.add_line(EVENT_FILE,event_line) 
    """
    
    
    
    def stopCam(self):
        """  Demande la fin de l'enregistrement et ferme l'objet caméra."""
        # permet d'arrêter l'enregistrement si on passe par le bouton stop"
        self._boucle = False
              
    def closeCam(self):
        """Arrêt du GPS"""
        if self._gps_ok == True:
            self.gps.stop_thread()
        """Arrêt définitif de la caméra"""
        self._end = True
        self._start_again.set()
        self._camera.stop()    
        logging.info("Caméra arrêtée")
        self._camera.close()
        logging.info("Caméra éteinte")
        if self.STEREO:
            self._camera2.stop()    
            logging.info("Caméra stéréo arrêtée")
            self._camera2.close()
            logging.info("Caméra stéréo éteinte")
        
            
    def restart(self):
        """démarre ou redémarre le thread"""
        self._boucle=True
        if self.is_alive():
            self._start_again.set()
        else:
            self.start()
    
