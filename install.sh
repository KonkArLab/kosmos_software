#!/bin/bash

echo "******************* Install Kosmos-config ********************* "

sudo apt update
sudo apt upgrade
sudo apt install git python3-pip virtualenv tree -y
# Activate Python3 env
source kosmosV3-env/bin/activate
# install required packages
cd kosmosV3-env
pip install -r requirements.txt

# create folder for install code from github
mkdir kospython

echo " --------------- End install Kosmos-camera ----------------------------"
reboot
