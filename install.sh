#!/bin/bash

#Effectuer une mise a jour la carte
sudo apt update
sudo apt upgrade
sudo apt autoremove

#Installation des packages python necessaires 
sudo apt install -y `cat requirements.txt`
sudo pip install sounddevice --break-system-package

#Desactivation du bluetooth (raisons énergétiques)
sudo systemctl disable bluetooth

# Copier du fichier kosmos_system.ini
sudo cp -n /home/$USER/kosmos_software/kosmos_system_template.ini /home/$USER/kosmos_system.ini 
sudo chown $USER:$USER /home/$USER/kosmos_system.ini

#Creation du fichier de lancement
cd
echo "#!/bin/bash" > lancement_kosmos.sh

#Ajout de la commande de lancement du programme
sudo echo "sleep 20

# Demarrage du serveur
cd /home/$USER/kosmos_software/frontend
sudo python3 -m http.server 80 &

#Lance kosmos_main.py 
cd /home/$USER/kosmos_software/kosmos-env
sudo python3 kosmos_main.py" >> lancement_kosmos.sh

#Rendre le lancement.sh executable
sudo chmod 755 lancement_kosmos.sh

#Activation de i2c (capteurs), serial (GPS) et du vnc (communication)
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_serial_hw 0
sudo raspi-config nonint do_serial_cons 1


#Ajout de la ligne de commande dans crontab qui permet le lancement au demarrage et création d'un dossier log
mkdir -p /home/$USER/logfile_kosmos
(sudo crontab -l; echo @reboot sudo bash -c '/home/'"$USER"'/lancement_kosmos.sh >> "/home/'"$USER"'/logfile_kosmos/$(date +\%Y-\%m-\%d_\%Hh\%Mm\%Ss).log" 2>&1';) | uniq - | sudo crontab
sudo crontab -l

exit 0
