sudo nmcli connection modify "EthernetPort" \
ipv4.addresses "" \
ipv4.gateway "" \
ipv4.dns "" \
ipv4.method auto

sudo nmcli connection down "EthernetPort"
sudo nmcli connection up "EthernetPort"
