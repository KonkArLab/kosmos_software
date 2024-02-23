# kosmos software

Lors de l'installation une connection filaire est recommandée
<br></br>

Installer Debian bullseye 32 bit pour Raspberry Pi 4 sur la carte sd à partir de l'imageur Raspberry Pi
Pour cela:  
Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/) sur votre PC
Choisisser le modèle de carte : Raspberry Pi 4
Choisisser le système d'exploitation : Debian bullseye 32 bit
Choisisser le l'emplacement de stockage : votre carte SD
Lors de la recherche de Wifi n'appuyer pas sur Skip mais sur Next même si vous êtes en filaire sinon les mises à jour ne seront pas effectuées
<br></br>

Sur un PC, remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software 
<br></br>

Démarrer la Raspberry Pi avec la carte SD et effectuer la première installation
<br></br>

Ouvrir un terminal et taper la commande suivante:
```
sudo raspi-config
```
<br></br>

choisir dans le menu:
```
6 Advanced Options
AA Network Config -> NetworkManager
```
<br></br>

ne pas reboot tout de suite :
```
3 Interface options
I1 Legacy Camera -> enable
```
Effectuer le reboot
<br></br>

Aller dans l'onglet Wifi, Advanced Options
Créer un Wifi Hotspot et lui donner un nom.
Même si la connection se fait automatiquement retourner dans l'onglet Wifi, Modifier ensuite les connections.
Choisir le réseau Hotspot.
Aller dans l'onglet Général et cocher "Connect Automatically with priority" cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot
Enregistrer
<br></br>

Mettre le dossier kosmos_software dans le home (via le git ou par copie depuis une clé usb)
Dans un terminal taper les commandes suivantes:
```
git clone https://github.com/KonkArLab/kosmos_software.git		//copie le dossier kosmos_software
cd kosmos_software												//ouvre le dossier kosmos_software
git checkout Refonte_fromIMT2									//change de branche et vous place sur la branch "Refonte_fromIMT2"
```
<br></br>

Ouvir un terminal et taper :
```
cd kosmos_software
sudo chmod 755 install.sh										//""
sh install.sh
```													//""
<br></br>

Brancher la clé usb pour le stockage des données. Elle peut être vide ou contenir déjà un kosmos_config.ini, CSV et Video.
<br></br>

Sur votre téléphone dans un navigateur web entrée l'adresse 10.42.0.1 , cela vous dirigera vers l'interface de commande du KOSMOS
<br></br>
