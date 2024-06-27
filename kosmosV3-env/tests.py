'''
from GPS import *
from time import sleep

gps = GPS()

sleep(2)

gps.start()

sleep(2)

print(f'{(gps.get_latitude()):.5f}')

sleep(2)

gps.pause()

sleep(5)

gps.restart()

sleep(2)

print(gps.get_longitude())

sleep(1)

gps.stop_thread()
'''
import os

response=dict()
strr="ls -l -R /media/kosmos/BBEC-1946/KOS_BRE240627"
stream =os.popen(strr)       
streamOutput = stream.read()
strRef=streamOutput.split('./')
strRef2=strRef[0].split('\n\n')

outputList=[]
for i in range(1,len(strRef2)): 
    strRef3=strRef2[i].split('\n')
    ligne1=strRef3[0][-7:-1] # premier sous dossier
    lignes=strRef3[2][0:11]
             
    listTemp = strRef2[1].split(lignes)[1:]
    for e in listTemp:
        d=dict()
        data=e.split()
        d["size"]="{:.4f}".format(int(data[3])/(1024**2))
        d["month"]=data[4]
        d["day"]=data[5]
        d["time"]=data[6]
        d["fileName"]=ligne1+'/'+data[7]
        outputList.append(d)

response["data"]=outputList
response["status"]="ok"
print(response)

