# Raspberry Pi Playbooks

Collection of Ansible and Arduino scripts for setting up Raspberry Pi as a weather, security, and home automation hub.

# Components

### boot

Example files to copy to Raspberry Pi's ```boot``` partition in order to activate wireless network and ssh on the first boot.

Find out the correct IP address e.g. using ```arp -a``` command on a Mac and ssh to the server with default user (```pi```/```raspberry```). Change password and copy your ssh public key into ```.ssh/authorized_keys```. Now you are ready to execute Ansible playbooks.

[More about setting up headless Raspberry Pi](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)

### Playbooks

```
pip3 install ansible
```

Add your hosts into ```/etc/ansible/hosts```
```
[raspberrypi]
rpi
[raspberrypi:vars]
ansible_python_interpreter=/usr/bin/python3
```

Execute playbooks
```
cd playbooks
cp common.yml.{template,}
ansible-playbook setup.yaml
```

1. setup.yml 

Basic setup of Raspberry Pi 4b.

2. 4g.yaml

Configure Huawei E392 4G dongle.