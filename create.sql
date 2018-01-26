CREATE TABLE users (full_name VARCHAR (50) NOT NULL, username VARCHAR (50) NOT NULL, user_email VARCHAR(50) NOT NULL, password VARCHAR(50) NOT NULL, PRIMARY KEY (username));
CREATE TABLE vms (ip VARCHAR(50) NOT NULL, blocked boolean DEFAULT false, rancher_id VARCHAR(50) NOT NULL, vm_name VARCHAR(50) DEFAULT "VM1", PRIMARY KEY (ip));
vms
---
ip VARCHAR(50)
blocked boolean default=false
rancher_id VARCHAR(50)
vm_name VARCHAR(50)
primary
