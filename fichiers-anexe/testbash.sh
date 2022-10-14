# tests de modifications des fichiers system
echo "Hello bash !"
# modifier un ficher ou une ligne particulière
# sudao rm test.txt // supprimer les fichiers system
sudo touch test.txt

#sudo sed -i "1i\ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\n" >test.txt
sudo echo "Test ....." > test.txt
#update_config=1\n
#country=FR\n"
