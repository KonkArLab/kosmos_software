# Kosmos Software

<details open>
 <summary> Sommaire </summary>
 
  * [Installation](https://github.com/KonkArLab/kosmos_software/edit/Refonte_fromIMT2/READ_ME.md#installation)
  * [Mode d'emploi](https://github.com/KonkArLab/kosmos_software/blob/Refonte_fromIMT2)
    
</details>
<br>

## Installation
### Installation du système d'exploitation (OS) de la Raspberry  
Sur un PC :  
 - Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/)  
 - Choisisser le modèle de carte : Raspberry Pi 4  
 - Choisisser le système d'exploitation : Raspberry Pi OS (Legacy, 32 bit), Debian bullseye 32 bit  
 - Choisisser l'emplacement de stockage : votre carte SD  
<br>

Plusieurs fenêtres vont apparaître:  
 - Voulez-vous appliquer les réglages de personalisation de l'OS ?  
Clicker sur NON  
 - Toutes les données vont être supprimées  
Clicker sur OUI  
 - raspberry Pi Os a bien été écrit  
Clicker sur CONTINUER  

<br>

### Changement du fichier config
Toujours sur un PC,  
 - remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software

### Paramétrage de l'OS  
Lors de l'installation une connection filaire plutôt que wifi est recommandée.
  
Démarrer la Raspberry Pi avec la carte SD, la carte Raspberry est allumée lorsque les petites led clignotes. Le démarage peut prendre un peu de temps.  
Plusieurs fenêtres vont s'afficher:   
 - Welcome to Raspberry Pi Desktop !  
Clicker sur NEXT  
Choisir le pays : France  
Choisir la langue : French  
Choisir la time zone : Paris  
Clicker sur NEXT  
  
 - Create User  
Compléter les informations demandées (username, password)  
Clicker sur NEXT
  
 - Set up Screen  
Clicker sur NEXT
  
 - Select Wifi Network  
Clicker sur NEXT  
  
 - Update Software  
Clicker sur NEXT  
n'appuyer pas sur Skip mais sur Next sinon les mises à jour ne seront pas effectuées  
  
 - System is up to date  
Clicker sur OK  
  
 - Set up complete  
Clicker sur Restart  

### Première installation du logiciel KOSMOS
 - Ouvrir un terminal et taper la commande suivante:
```
sudo raspi-config		//Ouvre les paramètres de configuration de la raspberry
```
<br>

Un menu s'affiche, dans un terminal vous ne pouvez généralement utiliser que le clavier pour sélectionner les paramètres souhaités (pas de souris)  
déplacez vous avec les flèches et sélectionner les paramètres en appuyant sur Entrée  

 - Dans le menu, Choisir NetworkManager comme dispositif réseau:  
Aller dans "6 Advanced Options"  
pour le "AA Network Config" choisir "NetworkManager"	 
  
 - Ne pas redémarrer tout de suite, avant:  
Aller dans "3 Interface options"  
pour "I1 Legacy Camera" choisir "enable"	
  
 - Redémarrage de kosmos:  
Aller dans "Finish" puis sélectionner OUI  

### Choix de la connection
 - Aller dans l'onglet Wifi (icone avec deux flèches de sens inversées)  
 - Création d'un Wifi Hotspot:  
Aller dans "Advanced Options"  
Puis "Create Wifi Hospot"
Donner lui un nom    
Ne pas mettre de sécurité sur le réseau  
Clicker sur "Créer"    
  
 - Retourner dans l'onglet Wifi et modifier les paramètres de connection par défault   
Aller dans "Advanced options"  
Puis "Modifier les connections"    
Choisir le réseau Hotspot  
Sélectionner le réseau créé et aller dans les paramètres (icone en forme d'engrenage)
Aller dans l'onglet Général
Cocher "Connect Automatically with priority" cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot  
Clicker sur "Enregistrer"

### Importation du dossier software
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//copie le dossier kosmos_software
cd kosmos_software							//ouvre le dossier kosmos_software
git checkout Refonte_fromIMT2						//change de branche et vous place sur la branch "Refonte_fromIMT2"
```
<br>

```
sudo chmod 755 install.sh		//Rendre éxécutable le fichier install.sh
sh install.sh				//Exécuter le fichier install.sh
```  
<br>
Une question apparaît dans le terminal:  

 - Souhaitez-vous continuer ?[O/n]  
Appuyer sur Entrée pour continuer et finir l'éxécution de la commande précédente
  
### Stockage des données
 - Brancher la clé usb pour le stockage des données. Elle peut être vide ou déjà contenir kosmos_config.ini, CSV et Video.

Maintenant le système est opérationnel.  

## Mode d'emploi
### Processus de mise à l'eau
Pour déployer KOSMOS en mer suivre le [guide de mis en service](https://kosmos.fish/index.php/deployer/).

### Prise en main de l'Interface web
Une IHM(Interface Homme Machine) à été développée et permet de commander Kosmos depuis votre téléphone. Elle remplace les étapes à réaliser avec les aimants. (A noté que le fonctionnement avec les aimants est toujours opérationnel.)

Sur votre téléphone:
 - Connecter vous au réseau de la raspberry qui à été créé dans les étapes précedentes  
 - Dans un navigateur web entrée l'adresse 10.42.0.1 , permet d'accéder à l'interface de commande du KOSMOS


En haut de l'écran 3 onglets:
 * Camera
 * Records
 * Configuration

##### Camera
###### State
Affiche l'état dans lequel se trouve la camera  

 - STANDBY
 - UNKNOW
 - START
 - SHUTDOWN
 - WORKING

###### Buttons
 - `Start` démarerr un enregistrement vidéo
 - `Stop` arrête l'enregistrement vidéo en cours

###### Live video
 - `Start Live` affiche ce que voit la camera
 - `Stop Live` arrête l'affichage ce que voit la camera

###### ShutDown KOSMOS
 - `Shutdown` éteint kosmos

##### Records
Affiche le nom, la taille et l'heure de fin d'enregistrement des derniers fichiers vidéo.

##### Configuration
Permet de modifier des paramètre du système

