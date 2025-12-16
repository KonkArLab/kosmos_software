# Kosmos Software
<!--
<details open>
 <summary> Sommaire </summary>
 
  * [Installation](https://github.com/KonkArLab/kosmos_software/blob/dev_stereo2/README.md#installation)
  * [Mode d'emploi](https://github.com/KonkArLab/kosmos_software/blob/dev_stereo2/README.md#mode-demploi)
    
</details>
<br>
-->
## Installation du système d'exploitation (OS) de la Raspberry  
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

## Configuration générale de la RPi.  
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

<!--
> Set up Screen  
> - Cliquer sur `Next`
-->
  
> Select Wifi Network  
> - Cliquer sur `Next`  
  
> Update Software  
> - Cliquer sur `Next` (et non sur `Skip` sinon les mises à jour ne seront pas effectuées. Cette opération peut prendre quelques minutes.)  
  
> System is up to date  
> - Cliquer sur `Ok`  
  
> Set up complete  
> - Cliquer sur `Restart`  


## Création d'un point Hotspot pour l'application KosmosWeb
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


### [Rpi5 seulement] Opération pour préparer la Rpi au mode de consommation minimale pour le mode MICADO

#### Activation du mode veille profonde

- Dans un terminal taper la commande suivante:
```
sudo -E rpi-eeprom-config --edit
```
- Ajouter/modifier les lignes de telle sorte qu'il y ait:
```
POWER_OFF_ON_HALT=1
WAKE_ON_GPIO=0
```
- Sauvegarder les modifications en appuyant sur `Ctrl + Shift + o`
- Quitter le fichier en appuyant sur `Ctrl + Shift + x`
- Taper sur `Entrée`

#### Activation de la recharge de la batterie

- Dans un terminal taper la commande suivante pour ouvrir le fichier `config.txt`:
```
sudo nano /boot/firmware/config.txt
```
- Ajouter à la fin du fichier les lignes suivantes:
```
dtparam=rtc_bbat_vchg=3000000
```
- Sauvegarder les modifications en appuyant sur `Ctrl + Shift + o`
- Quitter le fichier en appuyant sur `Ctrl + Shift + x`
- Taper sur `Entrée`

## [Rpi4 seulement] Configuration de la RPi pour l'utilisation des ports RX TX pour le GPS

- Dans un terminal taper la commande suivante pour ouvrir le fichier `config.txt`:
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
- Taper sur `Entrée`


<!--
### Activation des ports Serial et du VNC

- Aller dans le menu principal (icone avec la framboise en haut à gauche de l'écran)
- Cliquer sur `Préférence` puis `Configuration du Raspberry Pi`
- Dans l'onglet `Interface`
- Passer le `VNC` à `Enable`
- Passer le `Port serial` à `Enable`
- Passer le `Serial Console` à `Disable`
- Redémarrer enfin la Rpi.
-->

## Test de la caméra
Brancher la nappe à la RPI et à la caméra puis effectuer un redémarrage de la Rpi:
```
sudo reboot
```

On teste maintenant si la caméra fonctionne correctement. Pour ce faire, taper dans la console:
```
rpicam-hello --timeout 10000
```
Une fenêtre s'affichera normalement et contiendra le flux vidéo, et ce, pendant 2 secondes. À noter que si vous avez oté le filtre IR de la caméra, il se peut que la teinte de l'image soit rouge/orangée. 

Si aucune vidéo ne s'affiche, vérifier les branchements de la caméra. Redémarrer la RPi et recommencer ce test. 

## Importation et installation du logiciel KOSMOS depuis le Github 
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//Clone le dossier kosmos_software depuis le git
cd kosmos_software							//Ouvre le dossier kosmos_software
git checkout dev_ifremer
```

puis

<!-- sudo chmod 755 install.sh		//Rend exécutable le fichier install.sh -->

```
source install.sh				//Lance le fichier install.sh
```

Si des questions apparaissent  dans le terminal:  

> Souhaitez-vous continuer ?[O/n]

Taper `O` et appuyer sur `Entrée` pour finir l'exécution

## Mise-à-jour du fichier kosmos_system.ini
Ouvrir le fichier `kosmos_system.ini` qui se trouve au même niveau que le dossier `kosmos_software`.

Dans la section `[KOSMOS-system]` renseigner les champs suivants :
- `system` pour le nom du système, typiquement `K5` ou `KIMT`, etc.
- `version` pour la version du système, typiquement `3.0` ou `4.0`

Si besoin, mettre également à jour l'`increment`.  Si c'est le premier usage du système, il doit être à 1. Si le système a déjà été utilisé remettre l'incrément + 1 de la dernière vidéo. A noter que cet incrément doit être remis à 1 à chaque nouvelle année.  

## Stockage des données

Pour le stockage des données, deux choix s'ouvrent à vous : soit un stockage en local sur la carte SD, soit sur une clé USB. Si une clé USB est branchée, elle sera prioritaire. Si aucune clé usb n'est branchée, les fichiers seront stockées dans `/home/kosmos/kosmos_local_sd`.

<br>

**Le système est désormais opérationnel !** Pour le faire fonctionner, il suffit de redémarrer la Raspberry Pi ! Le logiciel kosmos va se lancer automatiquement et il sera possible d'interagir avec le système via la Wifi et l'interface Web. Son utilisation sera explicitée dans la section **Mode d'emploi**.



## Configuration à faire sur l'ordinateur avant le téléchargement des fichiers
Étape 1 : Accéder aux Propriétés Réseau
- Allez dans Paramètres (Settings).
- Cliquez sur Réseau et Internet (Network & Internet).
- Cliquez sur Paramètres réseau avancés (Advanced Network settings).
- Localisez votre adaptateur (Ethernet) et cliquez sur Afficher les propriétés supplémentaires (View additional properties).
##
Étape 2 : Modifier les Paramètres IPv4
- Dans la section "Propriétés Ethernet", vous verrez l'Adresse IP (IPv4 address) et le Masque de sous-réseau (IPv4 mask) actuels.
- Cliquez sur le bouton Modifier (Edit) à côté de la section "Attribution d'IP" (IP assignment).
- Changez le mode d'attribution d'IP de Automatique (DHCP) à Manuel (Manual).
#
Étape 3 : Saisir les Paramètres Manuels
- Activez le bouton bascule IPv4.
- Remplissez le champ Adresse IP (IP address) avec 192.168.10.1
- Remplissez le champ Masque de sous-réseau (Subnet mask) avec 255.255.255.0
- Passerelle (Gateway) : laisser vide
- DNS préféré (Preferred DNS) : laisser vide
- Cliquez sur Enregistrer (Save)


