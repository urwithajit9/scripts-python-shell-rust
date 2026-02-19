
    #!/bin/bash

    # Ping Forge With Provisioning Updates
    function provisionPing {
        curl --insecure --data "server_id=$2&type=$1&status=$3" https://backend.scrapeops.io/v1/servers/provisioning/callback
    }

    apt_wait()  {
            while fuser /var/lib/dpkg/lock >/dev/null 2>&1 ;
            do
            echo "Waiting: dpkg/lock is locked..." sleep 5
        done
            while fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 ;
            do
            echo "Waiting: dpkg/lock-frontend is locked..." sleep 5
        done
            while fuser /var/lib/apt/lists/lock >/dev/null 2>&1 ;
            do
            echo "Waiting: lists/lock is locked..." sleep 5
        done

    #	if [ -f /var/log/unattended-upgrades/unattended-upgrades.log ];
    #        	then
    #		while
    #			fuser /var/log/unattended-upgrades/unattended-upgrades.log >/dev/null 2>&1 ;
    #        	do
    #			echo "Waiting: unattended-upgrades is locked..." sleep 5 done
    #	fi
    }




    if [[ $EUID -ne 0 ]];
    then
        echo "This script must be run as root."
        exit 1
    fi

    UNAME=$(awk -F= '/^NAME/{print $2}' /etc/os-release | sed 's/\"//g')

    if [[ "$UNAME" != "Ubuntu" ]];
    then
        echo "ScrapeOps only supports Ubuntu 20.04 or 22.04"
        exit 1
    fi

    if [[ -f /root/.scrapeops-provisioned ]];
    then
        echo "This server has already been provisioned by ScrapeOps."
        echo "If you need to re-provision, you may remove the /root/.scrapeops-provisioned file and try again."
        exit 1
    fi

    #Step 1 complete
    provisionPing server-vm 590660 1


    # Upgrade The Base Packages
    export DEBIAN_FRONTEND=noninteractive
    apt-get update apt_wait
    apt-get upgrade -y apt_wait
    apt install whois


    # Add A Few PPAs To Stay Current
    apt-get install --allow-remove-essential --allow-change-held-packages software-properties-common


    ##### Step 2 complete #####
    provisionPing server-vm 590660 2


    # Disable Password Authentication Over SSH
    sudo sed -i -e "s/PasswordAuthentication yes/PasswordAuthentication no/g" /etc/ssh/sshd_config

    #enable ssh-rsa - needed for ubuntu 22.04+
    echo 'PubkeyAcceptedKeyTypes +ssh-rsa' >> /etc/ssh/sshd_config

    # Restart SSH
    ssh-keygen -A
    service ssh restart

    # Set The Hostname If Necessary
    echo "Megaproject" > /etc/hostname
    sed -i "s/127\.0\.0\.1.*localhost/127.0.0.1 Megaproject.localdomain Megaproject localhost/" /etc/hosts
    hostname "Megaproject"

    # Set The Timezone #
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime

    # Create The Root SSH Directory If Necessary
    if [ ! -d /root/.ssh ]
    then
        mkdir -p /root/.ssh touch /root/.ssh/authorized_keys
    fi


    # Check Permissions Of /root Directory
    chown root:root /root
    chown -R root:root /root/.ssh
    chmod 700 /root/.ssh
    chmod 600 /root/.ssh/authorized_keys

    # Setup ScrapeOps User
    useradd scrapeops
    mkdir -p /home/scrapeops/.ssh
    mkdir -p /home/scrapeops/.scrapeops
    adduser scrapeops sudo


    # Setup Bash For ScrapeOps User
    chsh -s /bin/bash scrapeops
    cp /root/.profile /home/scrapeops/.profile
    cp /root/.bashrc /home/scrapeops/.bashrc

    # Set The Sudo Password For ScrapeOps
    PASSWORD=$(mkpasswd -m sha-512 a7b6eae16ad49aa6)
    usermod --password $PASSWORD scrapeops


    # Build Formatted Keys & Copy Keys
    cat > /root/.ssh/authorized_keys << EOF
    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDyjWXHQy7NXIjB4MivqujK+UaulUsa3AEDYTVsD44YwXYADzTgb/lCdSBIid/i5EaIXt7x9/sh5Tt5Tl0PHHJhCuMXgEjQtMTt4V+PyGOAnB/aFPrGPQ8xDigUgzeoc/VmL9O3mBuegkVsBS4+ScwzSaA2dePCKAhtdE92SWae5a/0gayA2BgHXoH0S5B/6CV20TnhLQxmqTkmh4mGIls/ROToqoX1wawaAxuOc4+tJIAp97AXoDBYy3z6EEMJS+u3DBaGTXLu8KjOSEjS7mLMbG//xlogZRDhWJoOtuZhdtG7GPRoLH4UIQsvB++3UiX6lSupuIANSI060sYT7OIY/a25AL4dO7O4WW4/IqnpdUqiQfeJCU//0J7yf/o5BkDysDEQev9QPT84zFbedOdWisQ+fF44CJp+ZTpKLs1kT58aaBqz5u0APlLnzzKdgQRRnhW5Y9/gFVWtatHoQZLNtR8lyLpOh4p6J76Jj2hvy/K5QULxLPtzj1/ya1HYE7k= root@ubuntu-s-2vcpu-4gb-lon1-01
EOF
#ABOVE EOF MUST STAY IN THIS POSITION - Bash is sensitive to leading whitespace

    cp /root/.ssh/authorized_keys /home/scrapeops/.ssh/authorized_keys


    # Create The Server SSH Key
    ssh-keygen -f /home/scrapeops/.ssh/id_rsa -t rsa -N ''
    # Copy Source Control Public Keys Into Known Hosts File
    ssh-keyscan -H github.com >> /home/scrapeops/.ssh/known_hosts
    ssh-keyscan -H bitbucket.org >> /home/scrapeops/.ssh/known_hosts
    ssh-keyscan -H gitlab.com >> /home/scrapeops/.ssh/known_hosts


    # Now Set Permissions For New User Folder
    chown -R scrapeops:scrapeops /home/scrapeops
    chmod -R 755 /home/scrapeops
    chmod 700 /home/scrapeops/.ssh/id_rsa
    chmod 600 /home/scrapeops/.ssh/authorized_keys


    #Step 3 complete
    provisionPing server-vm 590660 3


    # Configure Git Settings
    git config --global user.name "Ajit" && git config --global user.email "ajit.megaproject@gmail.com"

    #re-run update incase the initial one didn't work
    apt-get update

    # Install things required for the scraping frameworks
    apt-get -y install python3-venv
    apt-get -y install python3-pip
    apt-get -y install python3-dev
    apt-get -y install npm
    apt-get -y install nodejs
    apt-get -y install libxml2-dev libxslt-dev
    apt-get -y install libffi-dev
    apt-get -y install build-essential
    apt-get -y install libssl-dev

    # Step 4 complete
    provisionPing server-vm 590660 4


    #TODO - ADD CLEANUP SCRIPT TO REMOVE PROVISION SCRIPT
    # Add The Provisioning Cleanup Script Into Root Directory
    #cat > /root/cleanup.sh << 'EOF' #!/usr/bin/env bash

    # Add Scrapeops User To www-data Group
    usermod -a -G www-data scrapeops id scrapeops groups scrapeops apt_wait


    # Disable protected_regular
    sudo sed -i "s/fs.protected_regular = .*/fs.protected_regular = 0/" /usr/lib/sysctl.d/protect-links.conf
    sysctl --system

    # Setup Unattended Security Upgrades
    #apt-get install -y --force-yes unattended-upgrades
    #cat > /etc/apt/apt.conf.d/50unattended-upgrades << EOF Unattended-Upgrade::Allowed-Origins { "Ubuntu focal-security"; }; Unattended-Upgrade::Package-Blacklist { // };
    #EOF

    #cat > /etc/apt/apt.conf.d/10periodic << EOF APT::Periodic::Update-Package-Lists "1"; APT::Periodic::Download-Upgradeable-Packages "1"; APT::Periodic::AutocleanInterval "7"; APT::Periodic::Unattended-Upgrade "1";
    #EOF


    touch /root/.scrapeops-provisioned


    #Step 5 complete - provisioning completed
    provisionPing server-vm 590660 5

  