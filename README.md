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
 - Choisir le système d'exploitation : Raspberry Pi OS (64 bit), Debian Bookworm
 - Choisir pour emplacement de stockage votre carte SD  
<br>

Plusieurs fenêtres vont apparaître:  
> Voulez-vous appliquer les réglages de personnalisation de l'OS ?  
> - Cliquer sur `Non`


> Toutes les données vont être supprimées. 
> - Cliquer sur `Oui` et l'installation commence. Elle peut durer quelques minutes.

> Raspberry Pi Os a bien été écrit.  
> - Cliquer sur `Continuer`  

<br>

[comment]: <### Changement du fichier config>
[comment]: <Toujours sur un PC,  >
[comment]: < - Remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software du Github.>

### Premier démarrage de la RPi.  
Une connexion ethernet filaire plutôt que Wifi est recommandée.
  
 - Démarrer la Raspberry Pi avec la carte SD, la carte RPi est allumée lorsque les petites leds de la carte clignotent. Le démarrage peut prendre un peu de temps.  
Plusieurs fenêtres vont s'afficher:   
> Welcome to Raspberry Pi Desktop !  
> - Cliquer sur `Next`  
> - Choisir le pays : France  
> - Choisir la langue : French  
> - Choisir la time zone : Paris  
> - Cliquer sur `Next`    
  
> Create User  
> - Compléter les informations demandées. Mettre pour username `kosmos` et pour mot de passe `kosmos` 
> - Cliquer sur `Next`
  
> Set up Screen  
> - Cliquer sur `Next`
  
> Select Wifi Network  
> - Cliquer sur `Next`  
  
> Update Software  
> - Cliquer sur `Next` (et non sur `Skip` sinon les mises à jour ne seront pas effectuées. Cette opération peut prendre quelques minutes.)  
  
> System is up to date  
> - Cliquer sur `Ok`  
  
> Set up complete  
> - Cliquer sur `Restart`  

### Première installation du logiciel KOSMOS
 - Ouvrir un terminal et taper la commande suivante:
```
sudo raspi-config		//Ouvre les paramètres de configuration de la raspberry
```
<br>

Un menu s'affiche, utiliser le clavier pour sélectionner les paramètres souhaités (pas de souris).  
Se déplacer avec les flèches et sélectionner les paramètres en appuyant sur Entrée. 

 [comment]: <- Dans le menu, aller dans `6 Advanced Options` puis dans `AA Network Config` choisir `NetworkManager`	> 
  
 [comment]: <- Aller ensuite dans `3 Interface options`  >
 [comment]: <pour `I1 Legacy Caméra` choisir `enable`  >

 - Aller dans `3 Interface Options` puis dans `I2 VNC` choisir `Enable`	 
   
 - Aller dans `Finish` puis sélectionner `Oui`.   

### Création d'un point Hotspot pour l'application KosmosWeb
[comment]: <Une fois la RPi redémarrée,>   
- Aller dans l'onglet Wifi (icone avec deux flèches de sens inversées) pour créer un Hotspot Wifi :
- Aller dans `Advanced Options`  
- Cliquer sur `Create Wifi Hospot`  
- Lui donner un nom `KosmosWeb2` où 2 est un numéro permettant de distinguer les systèmes kosmos entre eux 
- Ne pas mettre de sécurité sur le réseau  
- Cliquer sur `Créer`  
 
 Modification des paramètres de connexion par défaut afin que le hotspot se lance automatiquement au démarrage de la Rpi. 
 
- Retourner dans l'onglet Wifi
- Aller dans `Advanced options`  
- Aller dans `Modifier les connexions`    
- Choisir le réseau Hotspot  
- Sélectionner le réseau créé `KosmosWeb2`  et aller dans les paramètres (icone en forme d'engrenage)
- Aller dans l'onglet `Général` tout à gauche.
- Cocher `Connect Automatically with priority`, cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot  
- Cliquer sur `Enregistrer`

### Importation du dossier software
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//Clone le dossier kosmos_software depuis le git
cd kosmos_software							//Ouvre le dossier kosmos_software
```
<br>

```
sudo chmod 755 install.sh		//Rend exécutable le fichier install.sh
sh install.sh				//Lance le fichier install.sh
```  
<br>
Une question apparaît dans le terminal:  

> Souhaitez-vous continuer ?[O/n]  
> - Appuyer sur `Entrée` pour continuer et finir l'exécution de la commande précédente
  
### Stockage des données

 - Brancher la clé USB pour le stockage des données. Une fois l'installation réalisée la clé contient les fichiers suivants.

![dossier cle usb](fichiers-annexe/dossier_cle_usb.png)

Le fichier kosmos_config.ini contient les paramètres de configuration du système. Ces paramètres seront visibles depuis l'interface web grâce à un ficher Javascript. [Explication](https://github.com/KonkArLab/kosmos_software/blob/Refonte_fromIMT2/READ_ME.md#configuration)  

Vos fichiers enregistrés avec kosmos seront sauvegarder dans les dossiers CSV et Video.
Les fichiers vidéos et csv ne sont pas effacés à chaque démarrage. Si vous avez déjà enregistré des vidéos elles resteront stockées dans ces fichiers. 

- Redémarrer enfin la RPi. Si au démarrage, la led verte de la carte électronique clignote c'est que le système est opérationnel.  

## Mode d'emploi
### Processus de mise à l'eau
Pour déployer KOSMOS en mer suivre le [guide de mise en service](https://kosmos.fish/index.php/deployer/).

### Prise en main de l'Interface web
Une IHM (Interface Homme Machine) a été développée et permet de commander Kosmos depuis un téléphone. Elle remplace les étapes à réaliser avec les aimants dans le guide de mise en service. (À noter que le fonctionnement avec les aimants est toujours opérationnel.)

Sur un téléphone:
 - Se connecter au réseau de la raspberry qui a été créé dans les étapes précédentes  
 - Dans un navigateur web entrer l'adresse 10.42.0.1 qui permet d'accéder à l'interface de commande du KOSMOS


En haut de l'écran il y a 3 onglets:
 * Camera
 * Records
 * Configuration

<img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_camera.jpg" width = 299> <img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_records.jpg" width = 300> <img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_config.jpg" width = 300>  
<br>

 
##### Camera
###### State
Affiche l'état dans lequel se trouve la caméra  

 - UNKNOW : état inconnu
 - STARTING : kosmos est en train de démarrer
 - STANDBY : kosmos est en attente
 - WORKING : kosmos entame l'enregistrement
 - STOPPING : kosmos termine l'enregistrement
 - SHUTDOWN : kosmos passe à l'arrêt total

###### Buttons
 - `Start` démarre un enregistrement vidéo
 - `Stop` arrête l'enregistrement vidéo en cours

###### Live video
 - `Start Live` affiche ce qu'observe la caméra. (Ce live vidéo ne fonctionne que dans l'état STANDBY.)
 - `Stop Live` arrête l'affichage de ce qu'observe la caméra

###### ShutDown KOSMOS
 - `Shutdown` éteint kosmos
<br>

##### Records
Affiche le nom, la taille et l'heure de fin d'enregistrement des derniers fichiers vidéos.
<br>

##### Configuration
Permet de modifier des paramètres du système  
Un fichier javascript vient lire le fichier kosmos_config.ini.  
Puis il va créer une liste avec les différents noms des paramètres écrits dans le fichier kosmos_config.ini. Les noms des paramètres seront associés à un label et les valeurs des paramètres seront associées à un input. Par défaut l'input est en "readonly" c'est à dire qu'il n'est pas modifiable. Pour pouvoir le modifier il faut appuyer sur le bouton `Modify` entrer la nouvelle valeur puis la sauvegarder avec `Save`. Une fois la valeur sauvegardée le fichier kosmos_config.ini se mettra à jour.  
Il est également possible de modifier les paramètres directement dans le fichier kosmos_config.ini.

 - 00_system_mode :
    * si 0 :  
    * si 1 :  
 - 01_system_record_button_gpio :
 - 02_system_stop_button_gpio :
 - 03_system_led_b :
 - 04_system_led_r :
 - 05_system_shutdown :
    * si 0 : lors du shutdown le programme s'arrête mais la Rpi reste allumée (c'est utile pour débugger.)
    * si 1 : lors du shutdown le programme s'éteint (privilégier ce mode sur le terrain)
 - 06_system_moteur :
    * si 0 : rotation du moteur désactivée
    * si 1 : rotation du moteur activée
<br>

 - 10_motor_esc_gpio :
 - 11_motor_power_gpio :
 - 12_motor_button_gpio :
 - 13_motor_vitesse_min : vitesse minimale du moteur utilisée lors de son armement
 - 14_motor_vitesse_favorite : vitesse nominale du moteur
 - 15_motor_pause_time : temps en seconde de pause entre les mouvements de rotation (typiquement 27 secondes pour le protocole STAVIRO)
<br>

 - 20_csv_step_time : temps en seconde avant la prochaine prise de données dans le fichier csv (typiquement 5 secondes)
 - 21_csc_file_name : début du nom des fichiers csv
<br>

 - 30_picam_file_name : début du nom des fichiers vidéos
 - 31_picam_resolution_x : résolution de l'image selon l'axe des x (typiquement 1920)
 - 32_picam_resolution_y : résolution de l'image selon l'axe des y (typiquement 1080)
 - 33_picam_preview :
    * si 0 : pas d'aperçu de ce qu'observe la caméra sur l'écran (préférer ce mode sur le terrain)
    * si 1 : affiche un aperçu de ce qu'observe la caméra sur l'écran (utile pour le développement et le débuggage)
 - 34_picam_framerate : nombre d'images enregistrées par seconde (typiquement 24)
 - 35_picam_record_time : temps d'enregistement en seconde (typiquement 1600 secondes)
 - 36_picam_conversion_mp4 :
    * si 0 : ne convertit pas les fichiers vidéos en mp4 et les laisse en h264.
    * si 1 : convertit les fichiers vidéos en mp4
 - 37_picam_awb :
    * si 0 : 
    * si 1 :
