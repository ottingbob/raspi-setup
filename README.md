### Setup

First we need to setup the pis with an operating system.

I used the Raspberry Pi imager with two different OS distros:
- Raspberry Pi OS Full 32-bit
- Ubuntu Server 20.04.2 LTS 64-bit

I have setup a `.env` file in `./env/.env` in order to hold config like:
- REGISTRY_HOST
- REGISTRY_PORT
- NFS_HOST
- HOST_SUBNET

For the monitoring I have a `scripts/mon.py` file to deploy out onto the
different hosts in the cluster.

I need to use a node-selector in the given deploy.yml k8s files in order
to have the right images go to the given hosts.

```
spec:
  template:
    spec:
      containers: []
      nodeSelector:
        kubernetes.io/hostname: <HOSTNAME>
        # OR you could do the following
        kubernetes.io/arch: arm64
```

To add an insecure docker host on the k3s side for kubelet add this into
the `/etc/rancher/k3s/registries.yaml` file:
https://rancher.com/docs/k3s/latest/en/installation/private-registry/

```
```

===

Warnings related to incorrectly unsecured registry:

```
  https://rancher.com/docs/k3s/latest/en/installation/private-registry/

  Warning  Failed     11s (x2 over 23s)  kubelet            Failed to pull image "$REGISTRY_HOST:$REGISTRY_PORT/pibuild:0.0.1.aarm64": rpc error: code = Unknown desc = failed to pull and unpack image "$REGISTRY_HOST:$REGISTRY_PORT/pibuild:0.0.1.aarm64": failed to resolve reference "$REGISTRY_HOST:$REGISTRY_PORT/pibuild:0.0.1.aarm64": failed to do request: Head "https://$REGISTRY_HOST:$REGISTRY_PORT/v2/pibuild/manifests/0.0.1.aarm64": x509: certificate signed by unknown authority
    Warning  Failed     11s (x2 over 23s)  kubelet            Error: ErrImagePull


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

### K8s nfs-client-provisioner

From ref [k8s nfs setup](https://michael-tissen.medium.com/setting-up-an-raspberrypi4-k3s-cluster-with-nfs-persistent-storage-a931ebb85737)

Download necessary files for deploying provisioner:

```
wget https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/raw/master/deploy/rbac.yaml
wget https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/raw/master/deploy/class.yaml
wget https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner/blob/master/deploy/deployment.yaml
```

Replace the nfs-server hostname and path:
```
```

##### Getting Proper Software

Can't remember if there is anything for k3s we need to get specifically

We need to get a few things in order to run other services:
- helm

Getting helm via [the docs on the instgllation](https://helm.sh/docs/intro/install/)

    $ curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
    $ chmod 700 get_helm.sh
    $ ./get_helm.sh

    # THIS CHART IS DEPRECATED... NEED TO FIGURE OUT HOW TO SWITCH TO:
    # https://github.com/kubernetes/ingress-nginx/tree/master/charts/ingress-nginx
    $ export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
    $ helm repo add stable https://charts.helm.sh/stable
    $ helm repo update
    $ helm install nginx-ingress stable/nginx-ingress --set controller.publishService.enabled=true

    # Cert Manager Installation
    $ curl -o 00-crds.yml -L https://github.com/jetstack/cert-manager/releases/download/v1.3.1/cert-manager.crds.yaml
    $ kubectl create namespace cert-manager
    $ helm repo add jetstack https://charts.jetstack.io
    $ helm install cert-manager jetstack/cert-manager --version v1.3.1

    # I had to end up setting something in config.json for docker to accept
    # an insecure registry. I don't know where this file lives on windows and
    # digging up the correct one ? there were multiple but eventually I just
    # edited it through docker desktop under the `Docker Engine` tab:
    "insecure-registries": ["$REGISTRY_HOST:$REGISTRY_PORT"]

    # Once everything is setup then verify
    $ curl --insecure https://$REGISTRY_HOST:$REGISTRY_PORT/v2/_catalog
    {"repositories":["pibuild"]}
    $ curl --insecure https://$REGISTRY_HOST:$REGISTRY_PORT/v2/pibuild/tags/list
    {"name":"pibuild","tags":["0.0.1.armv7l","0.0.1.aarm64","0.0.1"]}

Looking up how to deploy the [prometheus-operator](https://grafana.com/docs/grafana-cloud/quickstart/prometheus_operator/)


### Accessing the PIs

They will be assigned in the range 192.168.1.0/24

### Starting K3s

##### Server

Check out the k3s docs at the [k3s website](https://k3s.io)

    curl -sfL https://get.k3s.io | sh -

##### Agent

Run the ./get-k3s.sh script.
Run the ./k3s-agent-start.sh script.
TODO: Need to get a unit file on starting up the service automatically

### Setting up persistent storage

    # Plug in USB
    $ lsblk
    NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    sda           8:0    1 14.7G  0 disk
    └─sda1        8:1    1 14.7G  0 part

    # Make the directory
    mkdir /media/usbstick
    sudo mount -t vfat /dev/sda1 /media/usbstick/
    sudo mount -t vfat /dev/sda1 /media/usbstick/ -o gid=pi-nfs-users -o umask=002

    # Once we are mounted verify
    $ lsblk
    NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
    sda           8:0    1 14.7G  0 disk
    └─sda1        8:1    1 14.7G  0 part /media/usbstick

    # Write a file to the directory
    $ sudo mkdir /media/usbstick/everyone
    $ echo 'hello file' | sudo tee /media/usbstick/everyone/hello.txt
    hello file

    # Get NFS Server
    $ sudo apt install -y nfs-kernel-server
    $ systemctl status nfs-server

    # Tell NFS we want directories exported 
    $ cat /etc/exports <<<EOF
    /media/usbstick/everyone *(rw,sync,no_subtree_check)
    EOF

    # Re-export directories
    # -a     Export or unexport all directories.
    # -r     Reexport all directories
    $ sudo exportfs -ar

    # On a remote in the cluster
    $ sudo apt install -y nfs-common
    $ sudo mount -t nfs $NFS_HOST:/media/usbstick/everyone /mnt
    $ ls /mnt
    hello.txt

    # Write to a file by creating the group
    $ sudo groupadd -g 4321 pi-nfs-users
    $ getent group | grep pi
    pi-nfs-users:x:4321:
    $ sudo usermod -a -G pi-nfs-users ubuntu

    # Make a permanent entry for the mount
    # /etc/fstab
    $NFS_HOST:/media/usbstick/everyone /srv nfs rw,user,soft,x-systemd.automount 0 0


    ## TEST THIS LATER
    mkdir -p /opt/nfs/registry 
    /opt/nfs/registry $HOST_SUBNET(rw,sync,no_subtree_check,no_root_squash)
    sudo exportfs -ar


### Scripts

Getting other host IP Addresses
    # Get hosts using nmap
    # -sn (No port scan); Ping Scan
    $ nmap -sn 192.168.1.0/24

Temperature
    # Get the temperature on Rasbian
    $ /opt/vc/bin/vcgencmd measure_temp
    temp=35.5'C

    # Get temperature on Ubuntu
    $ sudo apt install -y lm-sensors
    $ sensors
    cpu_thermal-virtual-0
    Adapter: Virtual device
    temp1:        +32.1°C

Interacting with the Docker Registry
    # Get different image repositories
    $ curl -k https://$REGISTRY_HOST:$REGISTRY_PORT/v2/_catalog
    {
      "repositories": [
        "pibuild"
      ]
    }
    
    # Get image tags
    $ curl -sk https://$REGISTRY_HOST:$REGISTRY_PORT/v2/pibuild/tags/list | jq
    {
      "name": "pibuild",
      "tags": [
        "0.0.3.aarm64",
        "0.0.1.aarm64",
        "0.0.2.aarm64",
        "0.0.4.aarm64"
      ]
    }

