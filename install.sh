#!/bin/bash

echo "Begin install Kosmos-config"

# Installer les mises à jour de l'OS
sudo apt update -y 
sudo apt upgrade -y

# Installer des "dependencies"
sudo apt install python3-pip python3-venv pigpio -y

if [ ! -d env ]; then
    echo "Create Python virtuel env"
    # Création de l'environnement virtuel
    python3 -m venv env
fi

if [ -d env ]; then
    echo "Install Python libraries..."
    # Activation de l'environnement virtuel
    source env/bin/activate
    # Installation des packages
    pip install -U -r requirements.txt
fi

echo "End install Kosmos-config"
#reboot
