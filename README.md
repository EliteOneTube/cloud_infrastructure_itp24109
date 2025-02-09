# VirtualBox Cloud Infrastructure Setup

This guide provides step-by-step instructions to set up a VirtualBox VM with attached storage, RAID configuration, and OpenVPN setup. You can follow the command-line instructions for Linux-based systems or use the VirtualBox GUI on Windows for similar configurations.

---

## Prerequisites
Ensure you have the following:
- Ubuntu/Debian-based system (for command-line instructions) or Windows (for GUI setup).
- Administrative privileges.
- Internet connection.

---

## Section 1: Creating the Virtual Machine

### 1. Update and Upgrade System Packages (Linux)
```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Dependencies (Linux)
```bash
sudo apt install -y wget apt-transport-https software-properties-common
```

### 3. Install VirtualBox

#### On Linux:
```bash
sudo apt update
sudo apt install -y virtualbox
```

#### On Windows:
- Download VirtualBox from [Oracle VirtualBox Downloads](https://www.virtualbox.org/wiki/Downloads).
- Run the installer and follow the on-screen instructions.

### 4. Create a New Virtual Machine

#### Using Command Line (Linux):
```bash
VBoxManage createvm --name "cloud_infrastructure" --ostype "Ubuntu_64" --register
VBoxManage modifyvm "cloud_infrastructure" --memory 6192 --cpus 2 --nic1 nat
```

#### Using GUI (Windows):
1. Open VirtualBox.
2. Click on **New**.
3. Set the name to "cloud_infrastructure" and select **Ubuntu (64-bit)** as the OS type.
4. Allocate 6 GB RAM and 2 CPUs.
5. Follow the wizard to complete the creation.

### 5. Create and Attach Storage

#### OS Disk
```bash
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/os-disk.vdi --size 20000
```

#### Data Disks
```bash
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/data-disk1.vdi --size 32768
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/data-disk2.vdi --size 32768
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/data-disk3.vdi --size 32768
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/data-disk4.vdi --size 32768
VBoxManage createhd --filename ~/VirtualBox\ VMs/cloud_infrastructure/data-disk5.vdi --size 32768
```

#### Add SATA Controller
```bash
VBoxManage storagectl "cloud_infrastructure" --name "SATA Controller" --add sata
```

#### Attach Disks
```bash
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 0 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/os-disk.vdi
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 1 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/data-disk1.vdi
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 2 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/data-disk2.vdi
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 3 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/data-disk3.vdi
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 4 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/data-disk4.vdi
VBoxManage storageattach "cloud_infrastructure" --storagectl "SATA Controller" --port 5 --device 0 --type hdd --medium ~/VirtualBox\ VMs/cloud_infrastructure/data-disk5.vdi
```

#### Using GUI (Windows):
1. Open the VM settings.
2. Go to **Storage** and attach each disk under the SATA controller.

### 6. Add Bootable ISO and Enable RDP

#### Download and Attach Ubuntu ISO
```bash
curl --output ubuntu.iso https://releases.ubuntu.com/24.04.1/ubuntu-24.04.1-desktop-amd64.iso
VBoxManage storagectl "cloud_infrastructure" --name "IDE Controller" --add ide
VBoxManage storageattach "cloud_infrastructure" --storagectl "IDE Controller" --port 0 --device 0 --type dvddrive --medium ubuntu.iso
```

#### Enable RDP and Start VM
```bash
VBoxManage modifyvm "cloud_infrastructure" --vrde on
VBoxManage startvm "cloud_infrastructure" --type headless
```

---

## Section 2: Configuring RAID and LVM

### 1. Install `mdadm`
```bash
sudo apt update
sudo apt install mdadm
```

### 2. Create RAID Devices

#### RAID 5 for Data Disks
```bash
sudo mdadm --create /dev/md0 --assume-clean --level=5 --raid-devices=3 /dev/sdb /dev/sdc /dev/sdd
```

#### RAID 1 for Data Disks
```bash
sudo mdadm --create /dev/md1 --assume-clean --level=1 --raid-devices=2 /dev/sde /dev/sdf
```

### 3. Configure LVM

#### Install LVM
```bash
sudo apt update
sudo apt install lvm2
```

#### Prepare Physical Volumes
```bash
sudo pvcreate /dev/md0
sudo pvcreate /dev/md1
```

#### Create Volume Group
```bash
sudo vgcreate vg_data /dev/md0 /dev/md1
```

#### Create Logical Volume
```bash
sudo lvcreate -L 95.89G -n lv_data vg_data
```

#### Format Logical Volume
```bash
sudo mkfs.ext4 /dev/vg_data/lv_data
```

#### Mount Logical Volume
```bash
sudo mkdir /mnt/lvm
sudo mount /dev/vg_data/lv_data /mnt/lvm
```

#### Add to `fstab`
```bash
echo '/dev/vg_data/lv_data /mnt/lvm ext4 defaults 0 0' | sudo tee -a /etc/fstab
```

---

## Section 3 - Setting Up OpenVPN

To set up OpenVPN and Easy-RSA, follow these steps:

### 1. **Update the package list and install OpenVPN and Easy-RSA:**
```bash
sudo apt update
sudo apt install openvpn easy-rsa
```

### 2. **Set up the Easy-RSA directory:**
```bash
make-cadir ~/easy-rsa
cd ~/easy-rsa
```

### 3. **Initialize the Public Key Infrastructure (PKI):**
```bash
./easyrsa init-pki
```

### 4. **Build the Certificate Authority (CA):**
```bash
./easyrsa build-ca
```

### 5. **Generate a certificate request for the server:**
```bash
./easyrsa gen-req server nopass
```

### 6. **Sign the server certificate request with the CA:**
```bash
./easyrsa sign-req server server
```

### 7. **Generate Diffie-Hellman parameters:**
```bash
./easyrsa gen-dh
```

### 8. **Generate a static key for TLS authentication:**
```bash
openvpn --genkey secret ta.key
```

### 9. **Copy the necessary files to the OpenVPN directory:**
```bash
sudo cp pki/ca.crt pki/issued/server.crt pki/private/server.key pki/dh.pem ta.key /etc/openvpn/
sudo cp /usr/share/doc/openvpn/examples/sample-config-files/server.conf /etc/openvpn/
```

### 10. **Edit the OpenVPN server configuration file (`/etc/openvpn/server.conf`):**
    - Add the following lines:
        ```
        ca ca.crt
        cert server.crt
        key server.key
        dh dh.pem
        ```
    - Enable TLS-auth by uncommenting and updating this line:
        ```
        tls-auth ta.key 0
        ```
    - Change the encryption cipher (optional but recommended for newer setups):
        ```
        cipher AES-256-CBC
        ```
    - Push DNS options (optional):
        ```
        push "redirect-gateway def1 bypass-dhcp"
        push "dhcp-option DNS 8.8.8.8"
        push "dhcp-option DNS 8.8.4.4"
        ```

### 11. **Start and enable the OpenVPN service:**
```bash
sudo systemctl start openvpn@server
sudo systemctl enable openvpn@server
```

### 12. **Enable IP forwarding:**
```bash
sudo nano /etc/sysctl.conf
```
- Add or uncomment the following line:
    ```
    net.ipv4.ip_forward = 1
    ```
- Apply the changes:
    ```bash
    sudo sysctl -p
    ```

### 13. **Set up IP tables for NAT and forwarding:**
```bash
sudo iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o enp0s3 -j MASQUERADE
sudo iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -s 10.8.0.0/24 -j ACCEPT
```

### 14. **Install and configure iptables-persistent to save the rules:**
```bash
sudo apt install iptables-persistent
sudo netfilter-persistent save
sudo netfilter-persistent reload
```

### 15. **Generate a certificate and key for the client:**
```bash
./easyrsa gen-req client1 nopass
./easyrsa sign-req client client1
```

### IMPORTANT: You need to port-forward UDP port 1194 on your router to the server's local IP address.

### 16. **Create the client configuration file:**
```bash
cp /usr/share/doc/openvpn/examples/sample-config-files/client.conf ~/client1.ovpn
```


### 17. **Edit the client configuration file (`~/client1.ovpn`):**
    - Specify the server's public IP address or domain name:
        ```
        remote YOUR_SERVER_IP 1194
        ```
    - Ensure the file includes these lines for security and encryption:
        ```
        ca ca.crt
        cert client1.crt
        key client1.key
        tls-auth ta.key 1
        ```

### 18. **Copy the required files to the client machine:** 
    - `ca.crt`
    - `client1.crt`
    - `client1.key`
    - `ta.key`
    - `client1.ovpn`
  
### 19. **Connect to the OpenVPN server:**
```bash
sudo openvpn --config client1.ovpn
```

### 20. **Set up the Python virtual environment and run the application:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    nohup python3 app.py &
    ```
