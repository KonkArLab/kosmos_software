sudo nmcli connection modify "Wired connection 1" \
ipv4.addresses "" \
ipv4.gateway "" \
ipv4.dns "" \
ipv4.method auto

sudo nmcli connection down "Wired connection 1"
sudo nmcli connection up "Wired connection 1"
