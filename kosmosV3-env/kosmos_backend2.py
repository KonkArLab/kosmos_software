import numpy as np
from flask_cors import CORS
from flask import Flask,request,make_response
from PIL import Image
import io
import os

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
        self.app.add_url_rule("/frame_stop", view_func=self.image_stop)

    def run(self) :
        logging.info("Server is running !")
        self.app.run(host="0.0.0.0",port=5000,debug=False)
            
    def state(self):
        return {
            "status" : "ok",
            "state" : str(self.myMain.state)
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
            return {
                "status" : "ok"
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
                self.myMain._conf.set_val(key,data[key])
            self.myMain._conf.update_file()
            self.myMain.thread_camera.closeCam()
            if self.myMain.PRESENCE_MOTEUR==1:
                del self.myMain.motorThread
            del self.myMain.thread_camera
            del self.myMain.thread_csv

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
        response["data"]=dict(self.myMain._conf.config["KOSMOS"])
        response["status"]="ok"
        return response  

    def getRecords(self):
        response=dict()
        strr="ls -l "+"'"+VIDEO_ROOT_PATH+"'"
        stream =os.popen(strr)
        streamOutput = stream.read()
        print(streamOutput)
        listTemp = streamOutput.split('-rw-r--r-- ')[1:]# attention ici... les fichiers video sont en permission -rw-r--r-- mais pourquoi ? ça fait buguer l'algo si ça change...
        print(listTemp)
        outputList=[]
        for e in listTemp:
            d=dict()
            data=e.split()
            d["size"]="{:.4f}".format(int(data[3])/(1024**2))
            d["month"]=data[4]
            d["day"]=data[5]
            d["time"]=data[6]
            d["fileName"]=data[7]
            outputList.append(d)
        response["data"]=outputList
        response["status"]="ok"
        print(response)
        return response

    def image(self):
        camera=self.myMain.thread_camera._camera
        buf=io.BytesIO()
        camera.capture_file(buf,format='jpeg')
        response=make_response(buf.getvalue())
        response.headers['Content-Type']='image/jpg'
        return response    

    def image_stop(self):
        #self.myMain.thread_camera._camera.stop()
        print('toto')
        return {
                "status" : "toto"
        }
        