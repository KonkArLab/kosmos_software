#!/bin/bash

#Montage clef USB
sudo mkdir /media/pi/00clef
sudo mount /dev/sda1 /media/pi/00clef
sudo chmod ugo+rwx /media/pi/00clef

#RTC Mise à jour de l'heure
sudo echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
#sudo hwclock -s

#Lancement programme principal de la caméra dés l'allumage du KOSMOS ( mettre en commentaire si on veut le démarrer depuis le terminal )
cd /home/pi/kospython
python3 /kosmosV3-env/kosmos_main.py
