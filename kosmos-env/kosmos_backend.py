import numpy as np
from flask_cors import CORS
from flask import Flask,request,make_response,jsonify
from PIL import Image
import io
import os
import json
import time
import subprocess
import re
from datetime import datetime

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from kosmos_state import KState
from kosmos_config import *

class Server:
    
    app = Flask(__name__)

    def __init__(self,myMain):
        self.myMain=myMain
        self._recording_start = None
        CORS(self.app)
        
        self.app.add_url_rule("/state", view_func=self.state)
        self.app.add_url_rule("/start", view_func=self.start, methods=['GET','POST'])
        self.app.add_url_rule("/stop", view_func=self.stop)
        self.app.add_url_rule("/shutdown", view_func=self.shutdown)
        self.app.add_url_rule("/getRecords", view_func=self.getRecords)
        self.app.add_url_rule("/changeConfig", view_func=self.changeConfig,methods=['POST'])
        self.app.add_url_rule("/getConfig", view_func=self.getConfig)
        self.app.add_url_rule("/frame", view_func=self.image)
        self.app.add_url_rule("/updateMetadata",view_func=self.update_metadata, methods=['POST']) 
        
        self.app.add_url_rule("/sensors", view_func=self.sensors)
        self.app.add_url_rule("/initSensors", view_func=self.initSensors)

        self.app.add_url_rule("/motorPlus", view_func=self.rotatePlus)
        self.app.add_url_rule("/motorMinus", view_func=self.rotateMinus)
        
        self.app.add_url_rule("/save", view_func=self.save)
        self.app.add_url_rule("/checkConversion", view_func=self.checkConversion)
        self.app.add_url_rule("/testLumen", view_func=self.testLumen)
        
        self.app.add_url_rule("/testIP", view_func=self.testIP)
        self.app.add_url_rule("/changeIP", view_func=self.changeIP)
        self.app.add_url_rule("/setPhoneGPS", view_func=self.setPhoneGPS, methods=['POST'])
        self.app.add_url_rule("/resetPhoneGPS", view_func=self.resetPhoneGPS, methods=['POST'])
        self.app.add_url_rule("/gpsStatus", view_func=self.gpsStatus)
        self.app.add_url_rule("/frame2", view_func=self.image2)
        self.app.add_url_rule("/getRecordsGPS", view_func=self.getRecordsGPS)
        self.app.add_url_rule("/setTime", view_func=self.setTime, methods=['POST'])
        self.app.add_url_rule("/maj", view_func=self.gitPull)

    def setTime(self):
        try:
            data = request.get_json(silent=True) or {}
            new_time = str(data.get("datetime", "")).strip()
            if not new_time:
                return jsonify({"status": "error", "message": "datetime manquant"}), 400
            subprocess.run(["timedatectl", "set-ntp", "false"], check=False)
            subprocess.run(["date", "-s", new_time], check=True)
            logging.info(f"Heure système synchronisée sur : {new_time}")
            
            # On regenere le bon dossier de campagne
            self.myMain._conf.createSurveyFile()

            return jsonify({"status": "ok", "time": new_time})
        
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def resetPhoneGPS(self):
        try:
            self.myMain.thread_camera._phone_gps_lat = None
            self.myMain.thread_camera._phone_gps_lon = None
            return jsonify({"status": "ok"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def gpsStatus(self):
        try:
            lat = self.myMain.thread_camera.gps.get_latitude()
            has_fix = lat is not None
        except:
            has_fix = False
        return jsonify({"has_fix": has_fix})

    def setPhoneGPS(self):
        try:
            data = request.get_json(silent=True) or {}
            lat = str(data.get("lat", ""))
            lon = str(data.get("lon", ""))
            if not lat or not lon:
                return jsonify({"status": "error", "message": "lat/lon manquants"}), 400
            self.myMain.thread_camera._phone_gps_lat = lat
            self.myMain.thread_camera._phone_gps_lon = lon
            logging.info(f"GPS téléphone enregistré : {lat}, {lon}")
            return jsonify({"status": "ok", "lat": lat, "lon": lon})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    def run(self) :
        logging.info("Server is running !")
        self.app.run(host="0.0.0.0",port=5000,debug=False)
            
    def state(self):
        is_working = str(self.myMain.state).split('.')[1] == 'WORKING'
        try:
            stereo = bool(self.myMain.thread_camera.STEREO)
        except Exception:
            stereo = False
        return {
            "status" : "ok",
            "state" : self.myMain._conf.systemName + " state is " + str(self.myMain.state).split('.')[1],
            "recording_start" : self._recording_start if is_working else None,
            "stereo" : stereo
        }
    
    def checkConversion(self):
        try:
            incrementt = self.myMain._conf.system.getint(INCREMENT_SECTION,"increment")-1
            str1 = self.myMain._conf.CAMPAGNE_PATH +f'{incrementt:04}'+"/"+f'{incrementt:04}'+".mp4" 
            str2 = self.myMain._conf.CAMPAGNE_PATH +f'{incrementt:04}'+"/"+f'{incrementt:04}'+".h264"
            str3 = self.myMain._conf.CAMPAGNE_PATH +f'{incrementt:04}'+"/"+f'{incrementt:04}'+"_stereo.mp4" 
            str4 = self.myMain._conf.CAMPAGNE_PATH +f'{incrementt:04}'+"/"+f'{incrementt:04}'+"_stereo.h264"
            if (os.path.exists(str1) and os.path.exists(str2)) or (os.path.exists(str3) and os.path.exists(str4)):
                checkConv = "Conversion en cours"
            else:
                checkConv = "Pas de conversion en cours"
        except:
            checkConv = "Pas de conversion en cours"
            
        return {
            "status" : "ok",
            "checkConversion" : checkConv 
        }
    
    def save(self):
        return {
            "status" : "ok",
            "save" : "Stockage des vidéos " + self.myMain._conf.sauvegarde 
        }
    
    def testLumen(self):
        try:
            if self.myMain.LIGHT_ENABLED == 1:
                self.myMain._light.on()
                time.sleep(1)
                self.myMain._light.off()
                return{
                "light" : "",
                }
            else:
                return{
                "light" : "Eclairage non activé",
                }
        except:
            return{
            "light" : "Eclairage défectueux",
            }
    
    # Moteur
    def rotatePlus(self):
        if self.myMain.PRESENCE_MOTEUR == 1:
            self.myMain.motorThread._state = 1
            self.myMain.motorThread.send_data(5)
            return{
                "motor" : "Avance"
            }
        else:
            return{
                "motor" : "Moteur non activé"
            }

    def rotateMinus(self):
        if self.myMain.PRESENCE_MOTEUR == 1:
            self.myMain.motorThread._state = 1
            self.myMain.motorThread.send_data(5)
            return{
                "motor" : "Recul"
            }
        else:
            return{
                "motor" : "Moteur non activé"
            }     
    
            
    def initSensors(self):
        self.myMain.thread_camera.init_lux()
        self.myMain.thread_camera.init_gps()
        self.myMain.thread_camera.init_tp()
        self.myMain.thread_camera.init_magneto()
        return {"init" : "Initialisation effectuée"}

    def sensors(self):
        # GPS
        try:
            LAT = self.myMain.thread_camera.gps.get_latitude()
            LONG = self.myMain.thread_camera.gps.get_longitude()
        except:
            LAT = "ERR"
            LONG = "ERR"
        # TP
        try:
            if self.myMain.thread_camera.pressure_sensor.read():
                press = self.myMain.thread_camera.pressure_sensor.pressure()
                PRESSURE = f'{press:.1f}'
                temp = self.myMain.thread_camera.pressure_sensor.temperature()  # Default is degrees C (no arguments)
                TEMPERATURE = f'{temp:.1f}'
            else:
                PRESSURE = "ERR"
                TEMPERATURE = "ERR"    
        except:
            PRESSURE = "ERR"
            TEMPERATURE = "ERR"
        # Magneto
        try:
            x, y, z, c = self.myMain.thread_camera.magneto_sensor.read()
            magneto_compass = f"{c:.0f}"
            MAGNETO = magneto_compass
        except:
            MAGNETO = "ERR"
        # LUX
        try:
            r, g, b = self.myMain.thread_camera.light_sensor.read()
            lux_r = f"{r}"
            lux_g = f"{g}"
            lux_b = f"{b}"
            LUX = 'R ' +lux_r + ' G ' + lux_b + ' B ' + lux_b
        except:
            LUX = "ERR"   
        # Batterie RTC
        try:
            result = subprocess.check_output(
                ["vcgencmd", "pmic_read_adc", "BATT_V"],
                text=True
            )
            RTC = str(result)
        except:
            RTC = "ERR"
        # Heure Rpi
        try:
            maintenant = datetime.now()
            heure = maintenant.strftime("%H:%M:%S")
            date = maintenant.strftime("%d/%m/%Y")
            time = date + " " + heure
        except:
            time = "ERR"   
            
        
        return{
            "latitude" : LAT,
            "longitude" : LONG,
            "pression" : PRESSURE,
            "temperature" : TEMPERATURE,
            "magneto" : MAGNETO,
            "RGB" : LUX,
            "rtc": RTC,
            "time": time
        }
    
    
    def start(self):
        if(self.myMain.state==KState.STANDBY):
            data = request.get_json(silent=True) or {}
            self.myMain.thread_camera.campaign_region = data.get("region",  "XX").strip().upper()
            self.myMain.thread_camera.campaign_zone      = data.get("zone",      "ZZ").strip().upper()
            self.myMain.thread_camera.campaign_type   = data.get("type",   "")
            self.myMain.thread_camera.campaign_boat      = data.get("boat",      "")
            self._recording_start = time.time()
            self.myMain.record_event.set()
            self.myMain.button_event.set()
            return {
                "status" : "ok",
                "recording_start" : self._recording_start
            }
        else :
            return {
                "status" : "error"
            }
    
    def stop(self):
        if(self.myMain.state==KState.WORKING):
            self.myMain.record_event.set()
            self.myMain.button_event.set()
            self.incr = self.myMain._conf.system.getint(INCREMENT_SECTION,"increment") 
            my_file = self.myMain.video_file
            
            try:
                metadata_path = self.myMain._conf.CAMPAGNE_PATH + my_file +"/" + my_file + ".json"
                while not os.path.exists(metadata_path):
                    time.sleep(1)
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {
                        "status" : "ok",
                        "metadata" : data
                    }
            except Exception as e:
                return {
                    "status" : "error"
            }
        else :
            return {
                "status" : "error"
            }
    
    def shutdown(self):
        if(self.myMain.state==KState.STANDBY):
            self.myMain.stop_event.set()
            self.myMain.button_event.set()
            return {
                "status" : "ok"
            }
        else :
            return {
                "status" : "error"
            }
    
    def changeConfig(self):
        if(self.myMain.state==KState.STANDBY):
            data = request.json
            for key in data:
                self.myMain._conf.config.set(CONFIG_SECTION,key,data[key])
            self.myMain._conf.update_config()

            # Arret des threads du systeme
            self.myMain.arretThreads()
                
            # Réinitialisation
            logging.info("REBOOOOOOOT !")
            self.myMain.init()
            self.myMain.button_event.set()
            return {
                "status" : "ok"
            }
        else:
            return {
                "status" : "error"
            }
        
    def getConfig(self):
        response=dict()        
        response["data"] = dict(self.myMain._conf.config[CONFIG_SECTION])
        response["status"]="ok"
        return response
    

    def getRecordsGPS(self):
        results = []
        campagne_path = self.myMain._conf.CAMPAGNE_PATH
        try:
            for folder in sorted(os.listdir(campagne_path)):
                json_path = os.path.join(campagne_path, folder, folder + '.json')
                if not os.path.isfile(json_path):
                    continue
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    obs = data.get('video_observation', {})
                    lat = obs.get('latitude', {}).get('value')
                    lon = obs.get('longitude', {}).get('value')
                    if lat is None or lon is None:
                        lat = obs.get('lat_tel', {}).get('value')
                        lon = obs.get('lon_tel', {}).get('value')
                    lat_f = float(lat)
                    lon_f = float(lon)
                    results.append({'name': folder, 'lat': lat_f, 'lon': lon_f})
                except Exception:
                    continue
        except Exception:
            pass
        return jsonify({'status': 'ok', 'data': results})

    def getRecords(self):
        response=dict()
        try:
            outputList=[]
            strr="ls -l -R " + self.myMain._conf.CAMPAGNE_PATH 
            stream =os.popen(strr)       
            streamOutput = stream.read()
            strRef=streamOutput.split('\n/')
            strRef2=strRef[1].split('\n-')

            for i in range(1,len(strRef)):
                strRef2=strRef[i].split('\n-')
                for j in range(1,len(strRef2)):
                    d=dict()
                    data=strRef2[j].split()
                    nomfichier,extension = os.path.splitext(data[8])
                    if (extension == '.mp4') or (extension == '.h264'):
                        d["size"]="{:.4f}".format(int(data[4])/(1024**2))
                        d["month"]=data[5]
                        d["day"]=data[6]
                        d["time"]=data[7]
                        d["fileName"]=data[8]
                        outputList.append(d)
        except:
           outputList=[] 
        response["data"]=outputList
        response["status"]="ok"
        return response


    def image(self):
        camera=self.myMain.thread_camera._camera
        buf=io.BytesIO()
        camera.options["quality"]=10 # compression pour fluidifier
        camera.capture_file(buf,format='jpeg')
        response=make_response(buf.getvalue())
        response.headers['Content-Type']='image/jpg'
        return response

    def image2(self):
        try:
            camera2 = self.myMain.thread_camera._camera2
        except AttributeError:
            return make_response('No second camera', 404)
        buf = io.BytesIO()
        camera2.options["quality"] = 10
        camera2.capture_file(buf, format='jpeg')
        response = make_response(buf.getvalue())
        response.headers['Content-Type'] = 'image/jpg'
        return response

    def get_metadata(self):
        metadata_path = GIT_PATH + "infoStationTemplate.json"
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return jsonify({
                "status": "success",
                "message": "ok",
                "metadata": data})

        except FileNotFoundError:
    
            return jsonify({
                "status": "error",
                "message": "Metadata file not found.",
                "data": "" 
            })

    
    def update_metadata(self):            
        my_file = self.myMain.video_file
        metadata_path = self.myMain._conf.CAMPAGNE_PATH +my_file+"/"+my_file +".json"
                
        data = request.json 
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return jsonify({
                "status": "success",
                "message": "Metadata saved successfully."
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to save metadata: {str(e)}"
            })
       
    def testIP(self):
        try:
            result = subprocess.check_output(
                ["nmcli", "-g", "ipv4.method", "connection", "show", "EthernetPort"],
                text=True
            )
            if result == "manual\n":
                return{
                "ip" : "Transfert de données actif",
                }
            elif result == "auto\n":
                return{
                "ip" : "Internet actif",
                }
            else:
                return{
                "ip" : "ERR",
                }
        except:
            return{
            "ip" : "ERR",
            }
    
    def changeIP(self):
        try:
            result = subprocess.check_output(
                ["nmcli", "-g", "ipv4.method", "connection", "show", "EthernetPort"],
                text=True
            )
            if result == "manual\n":
                subprocess.run(["sh", "/home/"+os.listdir("/home")[0]+"/kosmos_software/InternetActif.sh"])
                return{
                "ip" : "Internet activé",
                }
            elif result == "auto\n":
                subprocess.run(["sh", "/home/"+os.listdir("/home")[0]+"/kosmos_software/TransfertDonneesActif.sh"])
                return{
                "ip" : "Transfert de données activé",
                }
            else:
                return{
                "ip" : "ERR",
                }
        except:
            return{
            "ip" : "ERR",
            }

    def gitPull(self):
        # Bascule vers Internet actif 
        try:
            result = subprocess.check_output(
                ["nmcli", "-g", "ipv4.method", "connection", "show", "EthernetPort"],
                text=True
            )
            if result == "manual\n":
                subprocess.run(["sh", "/home/"+os.listdir("/home")[0]+"/kosmos_software/InternetActif.sh"])
            else:
                ...
        except:
            ...
        
        repo_path = "/home/"+os.listdir("/home")[0]+"/kosmos_software"
        try:
            # Vérifie l'état du dépôt
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
    
            # Si le dépôt contient des modifications
            if status.stdout.strip():
                print("Modifications locales détectées.")
                print("Restauration du dépôt...")
    
                subprocess.run(
                    ["git", "restore", "."],
                    cwd=repo_path,
                    check=True
                )
    
                # Supprime les fichiers/dossiers non suivis
                subprocess.run(
                    ["git", "clean", "-fd"],
                    cwd=repo_path,
                    check=True
                )
    
            # Effectue le pull
            result = subprocess.run(
                ["git", "pull"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )

            if result.sdout == 'Déjà à jour.\n':
                return {
                    "maj_txt" :  result.sdout,
                    }
            else : 
                return 
                    "maj_txt" :  "Git pull effectué, reboot pour finaliser la màj",
                }
        except:
            return {
                "maj_txt" : "ERR",
                }
