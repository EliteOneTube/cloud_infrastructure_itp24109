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

## Section 3: Setting Up OpenVPN

### 1. Install OpenVPN and Easy-RSA
```bash
sudo apt update
sudo apt install openvpn easy-rsa
```