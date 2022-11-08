#!/bin/bash

echo "Install Kosmos-config"

# Installer les mises à jour de l'OS
sudo apt update -y 
sudo apt upgrade -y

# Installer des "dependencies"
sudo apt install python3-pip python3-venv pigpio -y

# Création de l'environnement virtuel
python3 -m venv env
source env/bin/activate # Activation

# Installation des packages
pip install -r requirements.txt

echo "End install Kosmos-config"
reboot
