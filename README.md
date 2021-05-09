### Setup

First we need to setup the pis with an operating system.

I used the Raspberry Pi imager with two different OS distros:
- Raspberry Pi OS Full 32-bit
- Ubuntu Server 20.04.2 LTS 64-bit

```
# Rasbian Distro
$ cat /etc/os-release

PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"
NAME="Raspbian GNU/Linux"
VERSION_ID="10"
VERSION="10 (buster)"
VERSION_CODENAME=buster
ID=raspbian
ID_LIKE=debian
HOME_URL="http://www.raspbian.org/"
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"

# Ubuntu Server Distro
$ cat /etc/os-release

VERSION="20.04.2 LTS (Focal Fossa)"
ID=ubuntu
ID_LIKE=debian
PRETTY_NAME="Ubuntu 20.04.2 LTS"
VERSION_ID="20.04"
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
VERSION_CODENAME=focal
UBUNTU_CODENAME=focal
```

In order to get docker working we need to enable cgroups by making sure the setup files
are defined like so:

```
# Rasbian Distro
$ cat /boot/cmdline.txt
console=serial0,115200 console=tty1 root=PARTUUID=10d10611-02 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait quiet splash plymouth.ignore-serial-consoles cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1

# Ubuntu Server Distro
$ cat /boot/firmware/cmdline.txt
net.ifnames=0 dwc_otg.lpm_enable=0 console=serial0,115200 console=tty1 root=LABEL=writable rootfstype=ext4 elevator=deadline rootwait fixrtc cgroup_enable=cpuset cgroup_enable=memory cgroup_memory=1
```

##### Getting Proper Software

Can't remember if there is anything for k3s we need to get specifically

We need to get a few things in order to run other services:
- helm

Getting helm via [the docs on the instgllation](https://helm.sh/docs/intro/install/)

    $ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
    $ chmod 700 get_helm.sh
    $ ./get_helm.sh


### Accessing the PIs

They will be assigned in the range 192.168.1.0/24
73-75 for me

### Starting K3s

##### Server

Check out the k3s docs at the [k3s website](https://k3s.io)

    curl -sfL https://get.k3s.io | sh -

##### Agent

Run the ./get-k3s.sh script.
Run the ./k3s-agent-start.sh script.
TODO: Need to get a unit file on starting up the service automatically

