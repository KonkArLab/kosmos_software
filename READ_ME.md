# Kosmos Software

<details open>
 <summary> Sommaire </summary>
 
  * [Installation](https://github.com/KonkArLab/kosmos_software/blob/Refonte_fromIMT2/READ_ME.md#installation)
  * [Mode d'emploi](https://github.com/KonkArLab/kosmos_software/blob/Refonte_fromIMT2/READ_ME.md#mode-demploi)
    
</details>
<br>

## Installation
### Installation du système d'exploitation (OS) de la Raspberry  
Sur un PC :  
 - Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/)  
 - Choisir le modèle de carte : Raspberry Pi 4  
 - Choisir le système d'exploitation : Raspberry Pi OS (Legacy, 32 bit), Debian bullseye 32 bit  
 - Choisir pour emplacement de stockage votre carte SD  
<br>

Plusieurs fenêtres vont apparaître:  
 - Voulez-vous appliquer les réglages de personalisation de l'OS ?  
Cliquer sur NON  
 - Toutes les données vont être supprimées. 
Cliquer sur OUI et l'installation commence. Elle peut durer quelques minutes.
 - Raspberry Pi Os a bien été écrit.  
Cliquer sur CONTINUER  

<br>

### Changement du fichier config
Toujours sur un PC,  
 - Remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software du Git.

### Premier démarrage de la RPi.  
Lors de ce dernier, une connection filaire plutôt que wifi est recommandée.
  
Démarrer la Raspberry Pi avec la carte SD, la carte Raspberry est allumée lorsque les petites leds de la carte clignotent. Le démarrage peut prendre un peu de temps.  
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
Clicker sur NEXT (et non sur Skip sinon les mises à jour ne seront pas effectuées. Cette opération peut prendre quelques minutes.)  
  
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

Un menu s'affiche, vous ne pourrez y utiliser que le clavier pour sélectionner les paramètres souhaités (pas de souris).  
Se déplacer avec les flèches et sélectionner les paramètres en appuyant sur Entrée. 

 - Dans le menu, Choisir NetworkManager comme dispositif réseau:  
Aller dans "6 Advanced Options"  
pour le "AA Network Config" choisir "NetworkManager"	 
  
 - Aller ensuite dans "3 Interface options"  
pour "I1 Legacy Camera" choisir "enable"	
  
 - Redémarrage de kosmos:  
Aller dans "Finish" puis sélectionner OUI. Le système va redémarrer.  

### Création d'un point Hotspot pour l'application KosmosWeb
Une fois la RPi redémarrée,
 - Aller dans l'onglet Wifi (icone avec deux flèches de sens inversées)  
 - Création d'un Wifi Hotspot:  
Aller dans "Advanced Options"  
Puis "Create Wifi Hospot"
Lui donner un nom    
Ne pas mettre de sécurité sur le réseau  
Clicker sur "Créer"    
  
 - Retourner dans l'onglet Wifi et modifier les paramètres de connection par défault   
Aller dans "Advanced options"  
Puis "Modifier les connections"    
Choisir le réseau Hotspot  
Sélectionner le réseau créé et aller dans les paramètres (icone en forme d'engrenage)
Aller dans l'onglet Général tout à gauche.
Cocher "Connect Automatically with priority" cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot  
Clicker sur "Enregistrer"

### Importation du dossier software
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//Clone le dossier kosmos_software depuis le git
cd kosmos_software							//Ouvre le dossier kosmos_software
git checkout Refonte_fromIMT2						//Change de branche et vous place sur la branch "Refonte_fromIMT2"
```
<br>

```
sudo chmod 755 install.sh		//Rend éxécutable le fichier install.sh
sh install.sh				//Lance le fichier install.sh
```  
<br>
Une question apparaît dans le terminal:  

 - Souhaitez-vous continuer ?[O/n]  
Appuyer sur Entrée pour continuer et finir l'éxécution de la commande précédente
  
### Stockage des données
 - Brancher la clé usb pour le stockage des données. Elle peut être vide ou déjà contenir kosmos_config.ini, CSV et Video si elle a déjà été utilisée avec un système Kosmos.

Redémarrer enfin la RPi. Si au démarrage, la led verte de la carte électronique clignote c'est que le système est opérationnel.  

## Mode d'emploi
### Processus de mise à l'eau
Pour déployer KOSMOS en mer suivre le [guide de mise en service](https://kosmos.fish/index.php/deployer/).

### Prise en main de l'Interface web
Une IHM (Interface Homme Machine) a été développée et permet de commander Kosmos depuis un téléphone. Elle remplace les étapes à réaliser avec les aimants dans le guide de mise en service. (A noté que le fonctionnement avec les aimants est toujours opérationnel.)

Sur votre téléphone:
 - Connecter vous au réseau de la raspberry qui à été créé dans les étapes précedentes  
 - Dans un navigateur web entrée l'adresse 10.42.0.1 , permet d'accéder à l'interface de commande du KOSMOS


En haut de l'écran il y a 3 onglets:
 * Camera
 * Records
 * Configuration

##### Camera
###### State
Affiche l'état dans lequel se trouve la camera  

 - UNKNOW : etat inconnu
 - STARTING :kosmos est en train de démarrer
 - STANDBY : kosmos pret en attente
 - WORKING : kosmos entame l'enregistrement
 - STOPPING : kosmos termine l'enregistrement
 - SHUTDOWN : kosmos passe à l'arrêt total

###### Buttons
 - `Start` démarerr un enregistrement vidéo
 - `Stop` arrête l'enregistrement vidéo en cours

###### Live video
 - `Start Live` affiche ce qu'observe la camera
 - `Stop Live` arrête l'affichage ce qu'observe la camera

###### ShutDown KOSMOS
 - `Shutdown` éteint kosmos

##### Records
Affiche le nom, la taille et l'heure de fin d'enregistrement des derniers fichiers vidéos.

##### Configuration
Permet de modifier des paramètres du système
 - 00_system_mode :
    * si 0 :  
    * si 1 :  
 - 01_system_record_button_gpio :
 - 02_system_stop_button_gpio :
 - 03_system_led_b :
 - 04_system_led_r :
 - 05_system_shutdown :
    * si 0 : lors du shutdown le programme s'arrete
    * si 1 : lors du shutdown le programme s'éteint
 - 06_system_moteur :
    * si 0 : rotation du moteur désactivée
    * si 1 : rotation du moteur activée
<br>

 - 10_motor_esc_gpio :
 - 11_motor_power_gpio :
 - 12_motor_button_gpio :
 - 13_motor_vitesse_min : vitesse minimale du moteur
 - 14_motor_vitesse_favorite : vitesse de croissière du moteur
 - 15_motor_pause_time : temps en seconde de pause entre entre les mouvement de rotation
<br>

 - 20_csv_step_time : temps en seconde avant la prochaine prise de données dans le fichier csv
 - 21_csc_file_name : début du nom des fichiers csv
<br>

 - 30_picam_file_name : début du nom des fichiers vidéos (mettre un nom différent que pour les fichiers csv pour les enregistrer dans des dossiers séparés)
 - 31_picam_resolution_x : résolution de l'image selon l'axe des x
 - 32_picam_resolution_y : résolution de l'image selon l'axe des y
 - 33_picam_preview :
    * si 0 : pas d'apperçu de ce qu'observe la camera sur l'écran
    * si 1 : affiche un aperçu de ce qu'observe la camera sur l'écran
 - 34_picam_framerate : nombre d'image enregistrée par seconde
 - 35_picam_record_time : temps d'enregistement en seconde
 - 36_picam_conversion_mp4 :
    * si 0 : ne converti pas les fichiers vidéos en mp4
    * si 1 : converti les fichiers vidéos en mp4
 - 37_picam_awb :
    * si 0 : 
    * si 1 :
