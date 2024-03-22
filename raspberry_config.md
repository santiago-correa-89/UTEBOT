HARDWARE:

Raspberry Pi 4 8 Gb
SD card 64 Gb
Logitech Brios 4K

STEP 1
Boot Raspian operating system into the SD card and insert the SD card into the Raspberry PI. 

Raspian OP can be download from offcial site: https://www.raspberrypi.com/software/

STEP 2
SSH to your raspberry or connect a screen using a microHDMI connector.

STEP 3
sudo raspi-config
Access System Option -> Wireless LAN -> Select Country
After that REBOOT the raspberry

STEP 4
sudo apt update
sudo apt install hostapd % (allow use the raspberry act as a hotspot anntena)
sudo apt install dnsmask
sudo DEBIAN_FRONTEND=instalación apt no interactiva -y netfilter-persistente iptables-persistente

STEP 5
%Set access point
sudo systemctl unmask hostapd.service
sudo systemctl enable hostapd.serivce

STEP 6
%Edit the DHCP configs
sudo nano /etc/dhcpcd.conf

%At the end of the file add
interface wlan0
    static ip_address=10.20.1.1/24
    nohook wpa_supplicant

% remember save your changes

STEP 7
sudo nano /etc/sysctl.d/routed-ap.conf
net.ipv4.ip_forward=1

% remember save your changes

STEP 8 (set iptables)
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
sudo netfilter-persistent save

STEP 9 (set DHCP service ober router)
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.old
sudo touch /etc/dnsmasq.conf
sudo nano /etc/dnsmasq.conf

interface=wlan0
dhcp-range=10.20.1.5,10.20.1.100,255.255.255.0,300d
domain=wlan
address=/rt.wlan/10.20.1.1

% remember save your changes

STEP 10 (Create access point)
sudo touch /etc/hostapd/hostapd.conf
sudo nano /etc/hostapd/hostapd.conf

country_code=UY
interface=wlan0
ssid=utebot
hw_mode=a
channel=36
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=ddm-utebot
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP

% remember save your changes

sudo reboot

Now access point was created. An IP address will be provided to your device inside the UTEBOT WiFI network!

