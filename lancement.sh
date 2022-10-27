#!/bin/bash

#Dotenv
set -a; source .env; set +a

#Montage clef USB
sudo mkdir ${USB_ROOT_PATH}/00clef
sudo mount /dev/sda1 ${USB_ROOT_PATH}/00clef
sudo chmod ugo+rwx ${USB_ROOT_PATH}/00clef

#RTC Mise à jour de l'heure
sudo echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
#sudo hwclock -s

#Lancement programme principal de la caméra dés l'allumage du KOSMOS ( mettre en commentaire si on veut le démarrer depuis le terminal )
cd ~/kosmos_software
source env/bin/activate # Sécurité
python3 main.py
