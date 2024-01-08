Installer Debian bullseye 32 bit sur la carte sd à partir de l'imageur Raspberry Pi
Sur un PC, remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software 

Démarrer la Raspberry Pi avec la carte SD et effectuer la première installation

sudo raspi-config
6 Advanced Options
AA Network Config -> NetworkManager
ne pas reboot tout de suite :
3 Interface options
I1 Legacy Camera -> enable
Effectuer le reboot

 
Aller dans l'onglet Wifi, Advanced Options
Créer un Wifi Hotspot et lui donner un nom.
Modifier ensuite les connections.
Choisir le réseau Hotspot.
Aller dans l'onglet Général et cocher "Connect Automatically with priority"
Enregistrer



Mettre le dossier kosmos_software dans le home (via le git ou par copie depuis une clé usb)
git https://github.com/KonkArLab/kosmos_software/tree/dev_imt_groupe2/kosmos_software.git

Ouvir un terminal et taper :
cd kosmos_software
sudo chmod 755 install.sh
sh install.sh

Brancher la clé usb pour le stockage des données.
