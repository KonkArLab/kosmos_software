#!/bin/bash

#Effectuer une mise a jour la carte
sudo apt update

#Installation du dernier OS
sudo apt upgrade

#Telechargement de python 3
sudo apt install python3-pip

#Installation des packages necessaires 
cd kosmosV3-env
sudo pip install -r requirements.txt

#Recuperation du nom de la raspberry
nom_raspberry=$(whoami)
echo "$nom_raspberry"

#Creation du fichier de lancement
cd ..
echo "#!/bin/bash" > lancement.sh

#Ajout de la commande de lancement du programme
sudo echo "sleep 15
cd /home/$nom_raspberry/kosmos_software/kosmosV3-env
sudo python3 kosmos_main.py" >> lancement.sh

#Rendre le lancement.sh executable
sudo chmod 755 lancement.sh

#Activation de "Legacy camera" et "i2c"
cd ..
sudo raspi-config nonint do_i2c 0
#sudo raspi-config nonint do_camera 0

#Ajout de la ligne de commande dans crontab qui permet le lancement au demarrage et création d'un dossier log
mkdir -p /home/$nom_raspberry/kosmos_software/logfile
(sudo crontab -l; echo "@reboot sudo bash /home/$nom_raspberry/kosmos_software/lancement.sh > /home/$nom_raspberry/kosmos_software/logfile/log.txt 2>&1";) | uniq - | sudo crontab
sudo crontab -l

#Redémareage de la raspberry
sudo reboot

exit 0
