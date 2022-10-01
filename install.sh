#!/bin/bash

echo "******************* Install Kosmos-config ********************* "
sudo apt update
sudo apt upgrade
sudo apt install git python3-pip virtualenv -y

# create folder for install code from github
mkdir kospython
reboot
