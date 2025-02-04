import numpy as np
from flask_cors import CORS
from flask import Flask,request,make_response,jsonify
from PIL import Image
import io
import os
import json
import time


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

from kosmos_state import KState
from kosmos_config import *


class Server:
    
    app = Flask(__name__)

    def __init__(self,myMain):
        self.myMain=myMain
        CORS(self.app)
        
        self.app.add_url_rule("/state", view_func=self.state)
        self.app.add_url_rule("/start", view_func=self.start)
        self.app.add_url_rule("/stop", view_func=self.stop)
        self.app.add_url_rule("/shutdown", view_func=self.shutdown)
        self.app.add_url_rule("/getRecords", view_func=self.getRecords)
        self.app.add_url_rule("/changeConfig", view_func=self.changeConfig,methods=['POST'])
        self.app.add_url_rule("/getConfig", view_func=self.getConfig)
        self.app.add_url_rule("/frame", view_func=self.image)
        self.app.add_url_rule("/gps", view_func=self.position)
        self.app.add_url_rule("/updateMetadata",view_func=self.update_metadata, methods=['POST']) 


    def run(self) :
        logging.info("Server is running !")
        self.app.run(host="0.0.0.0",port=5000,debug=False)
            
    def state(self):
        return {
            "status" : "ok",
            "state" : str(self.myMain.state)
        }
    
    def position(self):
        try:
            LAT = str(self.myMain.thread_camera.gps.get_latitude())
            LONG = str(self.myMain.thread_camera.gps.get_longitude())
        except:
            LAT = "azrb"
            LONG = "strnage"
        return{
            "status" : "ok",
            "latitude" : LAT,
            "longitude" : LONG
        }
        
    def start(self):
        if(self.myMain.state==KState.STANDBY):   
            self.myMain.record_event.set() 
            self.myMain.button_event.set()
            return {
                "status" : "ok"
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
                #self.myMain._conf.set_val(key,data[key])
                self.myMain._conf.config.set(CONFIG_SECTION,key,data[key])
            self.myMain._conf.update_config()
            self.myMain.thread_camera.closeCam()
            
            # Désallocation des GPIOs avant reboot
            self.myMain._ledR.close()
            self.myMain._ledB.close()
            self.myMain.Button_Stop.close() 
            self.myMain.Button_Record.close()
            if self.myMain.PRESENCE_MOTEUR==1 and self.myMain._conf.systemVersion == "3.0":        
                self.myMain.motorThread.Relai_GPIO.close()
                self.myMain.motorThread.PWM_GPIO.close()
                self.myMain.motorThread.Button_motor.close()
            
            # Arrêt des Thread en cours
            if self.myMain.PRESENCE_MOTEUR==1:
                del self.myMain.motorThread
            if self.myMain.thread_camera.PRESENCE_HYDRO==1:
                del self.myMain.thread_camera.thread_hydrophone    
            del self.myMain.thread_camera
    
            # Réinitialisation
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
                json.dump(data, f, indent=4)
            return jsonify({
                "status": "success",
                "message": "Metadata saved successfully."
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to save metadata: {str(e)}"
            })
       
