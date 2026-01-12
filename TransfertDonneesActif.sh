sudo nmcli connection modify "Wired connection 1" \
ipv4.addresses 192.168.10.2/24 \
ipv4.gateway 192.168.10.1 \
ipv4.dns 192.168.10.1 \
ipv4.method manual

sudo nmcli connection down "Wired connection 1"
sudo nmcli connection up "Wired connection 1"
