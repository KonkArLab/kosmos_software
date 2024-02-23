# Kosmos Software

<div style='text-align: justify;'>

Lors de l'installation une connection filaire est recommandée
<br></br>

### Installer Debian bullseye 32 bit pour Raspberry Pi 4 sur la carte sd à partir de l'imageur Raspberry Pi  
Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/) sur votre PC  
Choisisser le modèle de carte : Raspberry Pi 4  
Choisisser le système d'exploitation : Debian bullseye 32 bit  
Choisisser le l'emplacement de stockage : votre carte SD  
Lors de la recherche de Wifi n'appuyer pas sur Skip mais sur Next même si vous êtes en filaire sinon les mises à jour ne seront pas effectuées  
<br>

### Changer le fichier config
Sur un PC, remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software
<br></br> 

### Première installation
Démarrer la Raspberry Pi avec la carte SD et effectuer la première installation
Ouvrir un terminal et taper la commande suivante:
```
sudo raspi-config		//Ouvre les paramètres de cofiguration de la raspberry
```
<br>

Choisir dans le terminal:
```
6 Advanced Options
AA Network Config -> NetworkManager		//Choisi NetworkManager comme dispositif réseau
```
<br>

Attention ne pas reboot tout de suite, avant aller dans:
```
3 Interface options
I1 Legacy Camera -> enable		//"Active la camera"
```
Effectuer le reboot
<br></br>

### Choix de la connection
Aller dans l'onglet Wifi, Advanced Options  
Créer un Wifi Hotspot et lui donner un nom.  
Même si la connection se fait automatiquement retourner dans l'onglet Wifi, Modifier ensuite les connections.  
Choisir le réseau Hotspot.  
Aller dans l'onglet Général et cocher "Connect Automatically with priority" cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot  
Enregistrer
<br></br>

### Importation du dossier software
Mettre le dossier kosmos_software dans le home (via le git ou par copie depuis une clé usb)  
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//copie le dossier kosmos_software
cd kosmos_software							//ouvre le dossier kosmos_software
git checkout Refonte_fromIMT2						//change de branche et vous place sur la branch "Refonte_fromIMT2"
```
<br>

Ouvir un terminal et taper :
```
cd kosmos_software
sudo chmod 755 install.sh		//""
sh install.sh				//""
```

<br>

### Stockage des données
Brancher la clé usb pour le stockage des données. Elle peut être vide ou contenir déjà un kosmos_config.ini, CSV et Video.
<br></br>

### Interface téléphone
Sur votre téléphone dans un navigateur web entrée l'adresse 10.42.0.1 , cela vous dirigera vers l'interface de commande du KOSMOS
<br></br>

</div>
