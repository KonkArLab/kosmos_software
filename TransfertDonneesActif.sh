sudo nmcli connection modify "EthernetPort" \
ipv4.addresses 192.168.10.2/24 \
ipv4.gateway 192.168.10.1 \
ipv4.dns 192.168.10.1 \
ipv4.method manual

sudo nmcli connection down "EthernetPort"
sudo nmcli connection up "EthernetPort"
