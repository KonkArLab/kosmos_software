#!/bin/bash
# Ligne 5,6,7,14 remplacer "kosmos2" par le nom d'utilisateur

#Montage clef USB
sudo mkdir /media/kosmos2/00clef
sudo mount /dev/sda1 /media/kosmos2/00clef
sudo chmod ugo+rwx /media/kosmos2/00clef

#RTC Mise à jour de l'heure
sudo echo ds3231 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
#sudo hwclock -s

#Lancement programme principal de la caméra dés l'allumage du KOSMOS ( mettre en commentaire si on veut le démarrer depuis le terminal )
cd /home/kosmos2/kosmosV3-env
python3 kosmos_main.py
