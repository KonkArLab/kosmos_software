#!/bin/bash

echo "Install Kosmos-config"

# Installer les mises à jour de l'OS
sudo apt update
sudo apt upgrade

sudo apt install python3-pip tree -y

# Création de l'environnement virtuel
python3 -m venv env
source env/bin/activate # Activation

# Installation des packages
pip install -r requirements.txt

echo "End install Kosmos-config"
reboot
