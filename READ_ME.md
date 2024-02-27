# Kosmos Software

<div style='text-align: justify;'>

Lors de l'installation une connection filaire plutôt que wifi est recommandée.
<br></br>

### Installer le système d'exploitation (OS) de la Raspberry  
Sur un PC :  
 - Installer [l'imageur Raspberry Pi](https://www.raspberrypi.com/software/)  
 - Choisisser le modèle de carte : Raspberry Pi 4  
 - Choisisser le système d'exploitation : Raspberry Pi OS (Legacy, 32 bit), Debian bullseye 32 bit  
 - Choisisser l'emplacement de stockage : votre carte SD  
<br>
Plusieurs fenêtres vont apparaître:
Voulez-vous appliquer les réglages de personalisation de l'OS ?  
NON  
Toutes les données vont être supprimées  
OUI  
raspberry Pi Os a bien été écrit  
CONTINUER  
<br>

### Changer le fichier config
Toujours sur un PC,  
 - remplacer le fichier config.txt du boot de la carte SD par celui présent dans le fichier kosmos_software
<br>

### Paramétrage de l'OS  

Démarrer la Raspberry Pi avec la carte SD, la carte Raspberry est allumée lorsque les petites led clignotes. Le démarage peut prendre un peu de temps.  
Plusieurs fenêtres vont s'afficher:   
Welcome to Raspberry Pi Desktop !  
NEXT  
Choisir le pays : France  
Choisir la langue : French  
Choisir la time zone : Paris  
NEXT  
  
Create User  
Compléter les informations demandées (username, mot de passe)  
NEXT
  
Set up Screen  
NEXT
  
Select Wifi Network  
NEXT  
  
Update Software  
NEXT  
n'appuyer pas sur Skip mais sur Next sinon les mises à jour ne seront pas effectuées  
  
System is up to date  
OK  
  
Set up complete  
Restart  

### Première installation du logiciel KOSMOS
Ouvrir un terminal et taper la commande suivante:
```
sudo raspi-config		//Ouvre les paramètres de configuration de la raspberry
```
<br>

Un menu s'affiche, dans un terminal vous ne pouvez généralement utiliser que le clavier pour sélectionner les paramètre souhaités (pas de souris)  
déplacez vous avec les flèches et sélectionner les paramètres en appuyant sur Entrée  

 - Dans le menu, Choisir NetworkManager comme dispositif réseau:  
6 Advanced Options  
AA Network Config -> NetworkManager	 
  
 - Attention ne pas reboot tout de suite, avant aller dans:  
3 Interface options  
I1 Legacy Camera -> enable	
  
 - Effectuer le reboot:  
Finish -> OUI  
<br>

### Choix de la connection
Aller dans l'onglet Wifi (icone avec deux flèches de sens inversées)  
 - Créer un Wifi Hotspot et lui donner un nom:  
Advanced Options  
Create Wifi Hospot  
Ne metter pas de sécurité sur le réseau  
Creer    
  
 - Même si la connection se fait automatiquement retourner dans l'onglet Wifi et modifier les paramètre de connection par défault 
Advanced options  
Modifier les connections    
Choisir le réseau Hotspot  
Sélectionner le réseau créé et aller dans les paramètres (icone en forme d'engrenage)
Aller dans l'onglet Général et cocher "Connect Automatically with priority" cela vous permettra de vous reconnecter directement lorsque le système effectuera un reboot  
Enregistrer
<br>

### Importation du dossier software
Mettre le dossier kosmos_software dans le home (via le git ou par copie depuis une clé usb)  
Dans un terminal taper les commandes suivantes:  
```
git clone https://github.com/KonkArLab/kosmos_software.git		//copie le dossier kosmos_software
cd kosmos_software							//ouvre le dossier kosmos_software
git checkout Refonte_fromIMT2						//change de branche et vous place sur la branch "Refonte_fromIMT2"
```
<br>

```
cd kosmos_software
sudo chmod 755 install.sh		//Rendre éxécutable le fichier install.sh
sh install.sh				//Exécuter le fichier install.sh
```  
<br>
Une question apparaît dans le terminal:  
Souhaitez-vous continuer ?[O/n]  
Entrée pour continuer  
  
### Stockage des données
Brancher la clé usb pour le stockage des données. Elle peut être vide ou contenir déjà un kosmos_config.ini, CSV et Video.  
  
### Interface web
Sur votre téléphone dans un navigateur web entrée l'adresse 10.42.0.1 , cela vous dirigera vers l'interface de commande du KOSMOS.  
  
</div>
