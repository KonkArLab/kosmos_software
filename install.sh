#!/bin/bash

#Effectuer une mise a jour la carte
sudo apt update

#Installation du dernier OS
sudo apt upgrade
sudo apt autoremove

#Telechargement de python 3
sudo apt install python3-pip

#Installation des packages necessaires 
cd kosmosV3-env
sudo pip install -r requirements.txt
sudo pip install flask_cors

#Recuperation du nom de la raspberry
nom_raspberry=$(whoami)
echo "$nom_raspberry"


#rendre exécutable  cle usb
#su chmod 755 kosmos_find_usb.sh
#Recuperation du nom de la clef USB
#USB_NAME=$(lsblk -o LABEL,MOUNTPOINT | grep "/media\|/mnt" | awk '{print $1}')
#echo "$USB_NAME"

#Creation du fichier de lancement
cd
echo "#!/bin/bash" > lancement_kosmos.sh

#Ajout de la commande de lancement du programme
sudo echo "sleep 20

# Demarrage du serveur
cd /home/$nom_raspberry/kosmos_software/frontend
sudo python3 -m http.server 80 &

#Lance kosmos_main.py 
cd /home/$nom_raspberry/kosmos_software/kosmosV3-env
sudo python3 kosmos_main.py" >> lancement_kosmos.sh

#Rendre le lancement.sh executable
sudo chmod 755 lancement_kosmos.sh

#Activation de "i2c"
sudo raspi-config nonint do_i2c 0

#Ajout de la ligne de commande dans crontab qui permet le lancement au demarrage et création d'un dossier log
mkdir -p /home/$nom_raspberry/logfile_kosmos
(sudo crontab -l; echo "@reboot sudo bash /home/$nom_raspberry/lancement_kosmos.sh > /home/$nom_raspberry/logfile_kosmos/log.txt 2>&1";) | uniq - | sudo crontab
sudo crontab -l

exit 0
