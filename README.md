# Kosmos Software

<details open>
 <summary> Sommaire </summary>
 
  * [Installation](https://github.com/KonkArLab/kosmos_software/blob/dev_stereo2/README.md#installation)
  * [Mode d'emploi](https://github.com/KonkArLab/kosmos_software/blob/dev_stereo2/README.md#mode-demploi)
    
</details>
<br>

## Installation
### Installation du système d'exploitation (OS) de la Raspberry  
Sur un PC :  
 - Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/)  
 - Choisir le modèle de carte : Raspberry Pi 4 (ou 5 selon le modèle)
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

### Activation du port Serial pour le GPS
#### Sur Rpi4
Modification du fichier config.txt

- Dans un terminal taper la commande suivante pour ouvrir le fichier config.txt:
```
sudo nano /boot/firmware/config.txt
```
- Ajouter à la fin du fichier les lignes suivantes:
```
dtoverlay=uart2
enable_uart=1
dtoverlay=disable-bt
```
- Sauvegarder les modifications en appuyant sur `Ctrl + Shift + o`
- Quitter le fichier en appuyant sur `Ctrl + Shift + x`

- Aller dans le menu principal (icone avec la framboise en haut à gauche de l'écran)
- Cliquer sur `Préférence` puis `Configuration du Raspberry Pi`
- Dans l'onglet `Interface`
- Passer le `VNC` à `Enable`
- Passer le `Port serial` à `Enable`
- Passer le `Serial Console` à `Disable`
- Redémarrer enfin la Rpi.

#### Sur Rpi5
- Dans un terminal taper :
```
sudo raspi-config
```
- Aller dans `3 Interface Options` puis dans `I6 Serial Port`
- Mettre `Oui` aux deux questions posées.
- Redémarrer enfin la Rpi.

### Importation du dossier software
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//Clone le dossier kosmos_software depuis le git
cd kosmos_software							//Ouvre le dossier kosmos_software
git checkout dev_stereo_merge_imt
```
<br>

```
sudo chmod 755 install.sh		//Rend exécutable le fichier install.sh
source install.sh				//Lance le fichier install.sh
```  
<br>
Une question apparaît dans le terminal:  

> Souhaitez-vous continuer ?[O/n]  
> - Appuyer sur `Entrée` pour continuer et finir l'exécution de la commande précédente

### Mise-à-jour du fichier kosmos_system.ini
Ouvrir le fichier `kosmos_system.ini` qui se trouve au même niveau que le dossier `kosmos_software`.

Dans la section `[KOSMOS-system]` renseigner les champs suivants :
- `system` pour le nom du système, typiquement `K5` ou `KIMT`, etc.
- `version` pour la version du système, typiquement `3.0` ou `4.0`

Si besoin, mettre également à jour l'`increment`.  Si c'est le premier usage du système, il doit être à 1. Si le système a déjà été utilisé remettre l'incrément + 1 de la dernière vidéo. A noter que cet incrément doit être remis à 1 à chaque nouvelle année.  
  
### Stockage des données

 - Brancher la clé USB pour le stockage des données. Elle peut être vide ou contenir déjà des dossiers des campagnes précédentes. Nous recommandons toutefois de repartir d'une clé vierge pour éviter une saturation mémoire de la clé usb. 
  
 - Redémarrer maintenant la RPi. Si au démarrage, la led verte de la carte électronique clignote c'est que le système est opérationnel. Si la clé était vierge, elle doit maintenant contenir un dossiers et un ficher texte :

Le fichier kosmos_config.ini contient les paramètres de configuration du système. Ces paramètres seront visibles depuis l'interface web grâce à un ficher Javascript. [Explication](https://github.com/KonkArLab/kosmos_software/blob/dev_stereo2/README.md#prise-en-main-de-linterface-web)  

Le dossier contenant les données associées à une journée de campagne s'appelle normalement date_system, typiquement `250403_IMT`. Dans ce dossier, seront présents d'autres dossiers correspondant à chaque enregistrement (passage de l'état STANDBY à WORKING). Ils auront pour nom l'increment, typiquement `0054` 

Chacun de ces dossiers contiennent une vidéo (voire deux si l'on filme en stéréo) et ses métadonnées. 
- Le fichier vidéo `increment.mp4` (et éventuellement )
- Un fichier `zone+annee+codestation.txt` qui stocke l'instant de chaque frame de la video.
- Un fichier `zone+annee+codestation.csv` qui stocke des paramètres de la caméra ainsi que les données T,P et position pendant la prise de vue.
- Un fichier `zone+annee+codestation.json` qui stocke les métadonnées de la prise de vue.
- Un fichier `Events.csv` qui stocke les évènements du sytème comme la rotation du moteur ou la mise à jour des gains AWB

A noter qu'un fichier `infoStation.csv` existe aussi dans le dossier de campagne journalière. Il rassemble les métadonnées de chaque vidéo prise durant la journée.

## Mode d'emploi

### Procédure de mise au point de la caméra
- Nettoyer toutes les surfaces avec un chiffon microfibre puis on remontera l'objectif Edmund sur le capteur. Ré-assembler enfin ce module optique sur le système.
- Pour faire la mise au point de la caméra, le système ne sera pas placé dans le caisson. On branchera par ailleurs un écran à la Raspberry pour visualiser ce que filme la caméra.
- Une fois l'écran branché, on allumera le système et on attendra que le système KOSMOS soit en STAND BY.
- Dans l'interface WEB, modifier le paramètre `05_SYSTEM_shutdown` pour le mettre à 0 et effectuer un `Reboot`. Aller ensuite dans l'onglet `Camera` et éteindre arrêter le système KOSMOS en appuyant sur `Shutdown`. (Cette manipulation permet d'arrêter le script KOSMOS sans éteindre la Rpi. La caméra peut ainsi être utilisée.)
- Dans le terminal, taper ```rpicam-hello --timeout 0 ``` Cette instruction permet d'afficher le preview. Pour le quitter il suffira de taper ```Ctrl + C ```
- Viser un objet à l'infini (par exemple le feuillage d'arbres au loin). Ouvrir à fond l'objectif (le petit point blanc devant 1.8) pour avoir une profondeur de champ minimale. Réaliser le focus sur l'objet avec la bague puis la bloquer solidement. Fermer enfin l'objectif à moitié (le petit point blanc sur 2.8) pour récupérer une meilleure profondeur de champ. Bloquer la bague d'ouverture dans cette position. Vérifier que le focus est toujours bon (le fait de serrer les bagues peut parfois les faire bouger.)
- Sortir du preview puis redémarrer la Raspberry Pi. Le soft kosmos va se remettre en route. Dans l'interface web, remettre le paramètre  `05_SYSTEM_shutdown` sur 1. Effectuer un `Reboot` puis éteindre le système avec un `Shutdown`.

### Processus de mise à l'eau
Pour déployer KOSMOS en mer suivre le [guide de mise en service](https://kosmos.fish/index.php/deployer/).

### Prise en main de l'Interface web
Une IHM (Interface Homme Machine) a été développée et permet de commander Kosmos depuis un téléphone. Elle remplace les étapes à réaliser avec les aimants dans le guide de mise en service. (À noter que le fonctionnement avec les aimants est toujours opérationnel.)

Sur un téléphone ou un ordinateur portable:
 - Se connecter au réseau  WiFi de la raspberry qui a été créé dans les étapes précédentes  
 - Dans un navigateur web entrer l'adresse 10.42.0.1 qui permet d'accéder à l'interface de commande du KOSMOS


En haut de l'écran il y a 3 onglets:
 * Camera
 * Records
 * Configuration
 * Checklist
   
<img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_camera.jpg" width = 299> <img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_records.jpg" width = 300> <img src="https://github.com/KonkArLab/kosmos_software/blob/9b9281c0ae14215c8ec4bbfffb5d7e90c7b0e229/fichiers-annexe/interface_config.jpg" width = 300>  
<br>

 
##### Camera
###### State
Affiche l'état dans lequel se trouve la caméra  

 - UNKNOW : état inconnu (signe d'un mauvais fonctionnement)
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

##### Configuration, à mettre à jour....
Permet de modifier des paramètres du système  
Un fichier javascript vient lire le fichier kosmos_config.ini.  
Puis il va créer une liste avec les différents noms des paramètres écrits dans le fichier kosmos_config.ini. Les noms des paramètres seront associés à un label et les valeurs des paramètres seront associées à un input. Par défaut l'input est en "readonly" c'est à dire qu'il n'est pas modifiable. Pour pouvoir le modifier il faut appuyer sur le bouton `Modify` entrer la nouvelle valeur puis la sauvegarder avec `Save`. Une fois la valeur sauvegardée le fichier kosmos_config.ini se mettra à jour.  
Il est également possible de modifier les paramètres directement dans le fichier kosmos_config.ini.

 - `00_SYSTEM_mode = 1` permet de permuter entre les modes de fonctionnement du KOSMOS, seul le mode STAVIRO [1] existe pour le moment.  
 - `01_SYSTEM_record_button_gpio = 17` adresse gpio du bouton début/arrêt de l'enregistrement 
 - `02_SYSTEM_stop_button_gpio = 23` adresse gpio du bouton d'arrêt du système
 - `03_SYSTEM_led_b = 4` adresse gpio de la LED verte
 - `04_SYSTEM_led_r = 18` adresse gpio de la LED rouge
 - `05_SYSTEM_shutdown = 1`  permet d'éteindre ou non la Rpi lorsque le bouton arrêt est pressé. 
    * si `0` lors du shutdown le programme s'arrête mais la Rpi reste allumée (utiliser ce réglage pour le debug ou le développement software)
    * si `1` lors du shutdown le programme s'éteint (privilégier ce mode sur le terrain)
 - `06_SYSTEM_moteur = 1`  Active ou désactive le moteur
    * si `0` Moteur désactivé
    * si `1` Moteur activé
 - `07_SYSTEM_tps_fonctionnement = 1800` Règle le temps en secondes avant l'extinction automatique du système. Ce réglage permet d'éviter un déchargement complet des batteries ce qui les rendrait inutilisables.
<br>

 - `10_MOTOR_esc_gpio = 22` adresse gpio de l'esc qui pilote le moteur (c'est un signal PWM)
 - `11_MOTOR_power_gpio = 27` adresse gpio du relai qui alimente le moteur
 - `12_MOTOR_button_gpio = 21` adresse gpio de l'ILS qui permet d'asservir la croix de Malte
 - `13_MOTOR_vitesse_min = 1000` vitesse minimale du moteur utilisée lors de son armement (peut-être inutile...)
 - `14_MOTOR_vitesse_favorite = 1350` vitesse nominale du moteur. A régler avant le départ en mission. Typiquement entre 1200 & 1600.
 - `15_MOTOR_pause_time = 27`  temps de pause en secondes entre les rotations (typiquement 27 secondes pour le protocole STAVIRO)
 - `16_MOTOR_inertie_time = 1000` temps en ms qui permet de décaler l'aimant d'asservissement du moteur suffisamment loin de l'ILS afin d'éviter son activation fortuite. A régler avant le départ en mission. Typiquement entre 500 et 2000.
 - `17_MOTOR_timeout = 5` temps de sécurité en s d'arrêt du moteur s'il n'a pas détecté l'ILS d'asservissement. A régler avant le départ en mission. Typiquement entre 5 et 10.

<br>

 - `20_CSV_step_time = 5` Temps d'échantillonnage en secondes des données CSV (heure, pression, T°)
 - `21_CSV_file_name = CSV_Kosmos2` début du nom des fichiers csv
<br>

 - `30_PICAM_file_name = Video_Kosmos2` début du nom des fichiers vidéos
 - `31_PICAM_resolution_x = 1920` résolution de l'image selon l'axe des x (typiquement 1920)
 - `32_PICAM_resolution_y = 1080` résolution de l'image selon l'axe des y (typiquement 1080)
 - `33_PICAM_preview = 0` Affiche ce que voit la caméra pendant qu'elle enregistre
    * si `0` pas d'aperçu (CHOISIR IMPERATIVEMENT CE MODE SUR LE TERRAIN)
    * si `1` affiche un aperçu de ce qu'observe la caméra sur l'écran (utile pour le développement et le débug car ne fonctionne qu'avec un lancement de kosmos_main.py via la terminal)
 - `34_PICAM_framerate = 24` nombre d'images enregistrées par seconde (typiquement 24)
 - `35_PICAM_record_time = 1600` temps d'enregistement en secondes (typiquement 1600 secondes) des séquences vidéos. Si le système doit filmer plus longtemps que ce temps d'enregistrement, la vidéo sera découpée en plusieurs séquences. Ceci permet d'éviter la perte de données si un arrêt brutal se produit.
 - `36_PICAM_conversion_mp4 = 1`  
    * si `0` ne convertit pas les fichiers vidéos en mp4 et les laisse en h264.
    * si `1` convertit les fichiers vidéos en mp4 et supprime les h264
 - `37_PICAM_awb = 0` permet de définir le mode de fonctionnement de l'Automatic White Balance (seul le mode 0 fonctionne pour le moment)
 - `38_PICAM_timestamp = 0` incruste ou non une horloge dans l'image
    * si `0` pas d'incrustation
    * si `1` incrustation
