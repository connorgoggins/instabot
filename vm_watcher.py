import mysql.connector
import time
import os
import requests
import utils
from requests.auth import HTTPBasicAuth

cnx = utils.get_db_connection()
cursor = cnx.cursor()

def create_vm():
    # POST rancher
    DO_TOKEN = os.getenv("DO_TOKEN", "")
    create_vm_payload = {
        "type": "host",
        "digitaloceanConfig": {
            "accessToken": DO_TOKEN,
            "image": "ubuntu-16-04-x64",
            "region": "nyc3",
            "size": "2gb",
            "sshKeyFingerprint": "",
            "sshKeyPath": "",
            "sshPort": "22",
            "sshUser": "root",
            "tags": "",
            "userdata": "",
            "type": "digitaloceanConfig"
        },
        "engineInstallUrl": "https://releases.rancher.com/install-docker/1.12.sh",
        "hostname": "dev-3",
        "labels": {
            "app": "instamaker"
        }
    }

    create_vm_url = "https://try.rancher.com/v2-beta/projects/1a1065894/host"
    rancher_creds = utils.get_rancher_creds()
    r = requests.post(
        create_vm_url,
        json=create_vm_payload,
        auth=HTTPBasicAuth(rancher_creds["username"], rancher_creds["password"]),
    )

    if r.status_code == 201:
        # ONLY INSERT IF RANCHER RETURNS RESULT
        # INSERT INTO vms ip, rancher_id, blocked=false
        data = r.json()
        rancher_id = data["id"]
        ip = ""
        blocked = "0"

        add_vm = ("INSERT INTO vms (ip, rancher_id, blocked) VALUES (\"%s\", \"%s\", %s)")
        data_vm = (ip, rancher_id, blocked)
        cursor.execute(add_vm, data_vm)
        cnx.commit()
    return

def delete_vm(rancher_id):
    # DELETE Request to rancher
    delete_vm_url = "https://try.rancher.com/v2-beta/projects/1a1065894/hosts/"+rancher_id
    rancher_creds = utils.get_rancher_creds()
    r = requests.delete(
        delete_vm_url, 
        auth=HTTPBasicAuth(rancher_creds["username"], rancher_creds["password"]),
    )
    if r.status_code == 200:
        # ONLY DELETE FROM DB only if RANCHER RETURNS 200
        # DELETE FROM vms WHERE rancher_id = rancher_id
        query = ("DELETE FROM vms WHERE rancher_id='" + rancher_id+"'")
        cursor.execute(query)
        cnx.commit()   
        return None
    else:
        return "Error deleting vm with rancher_id: "+str(rancher_id)
    

def update_vms_without_ip():
    query = ("SELECT ip, rancher_id FROM vms WHERE ip=''")
    cursor.execute(query)

    for (blank_ip, rancher_id) in cursor:
        ip, err = get_rancher_vm_ip(rancher_id)
        if err == None:
            set_vm_ip(rancher_id, ip)
        else
            print(err)

def get_rancher_vm_ip(rancher_id):
    # DELETE Request to rancher
    rancher_vm_url = "https://try.rancher.com/v2-beta/projects/1a1065894/hosts/"+rancher_id
    rancher_creds = utils.get_rancher_creds()
    r = requests.get(
        rancher_vm_url, 
        auth=HTTPBasicAuth(rancher_creds["username"], rancher_creds["password"]),
    )
    if r.status_code == 200:
       return (r.json()["agentIpAddress"], None)
    else:
        return ("", "Cannot get vm with rancher_id: "+str(rancher_id))

def create_vm_if_empty():
    # SELECT COUNT(*) FROM vms where blocked=0;
    query = ("SELECT COUNT(*) FROM vms WHERE blocked=0")
    cursor.execute(query)

    for result in cursor:
        if result[0] < 1:
            create_vm()

def set_vm_ip(rancher_id, ip):
    update_vm = ("UPDATE vms SET ip=\"%s\" WHERE rancher_id=\"%s\"")
    data_vm = (ip, rancher_id)
    cursor.execute(update_vm, data_vm)
    cnx.commit()
    return

def check_vms():
    create_vm_if_empty()
    query = ("SELECT * FROM vms WHERE blocked=1")
    cursor.execute(query)

    for (ip, blocked, rancher_id, vm_name) in cursor:
        err = delete_vm(rancher_id)
        if err == None:
            create_vm()
        else:
            print("Failed to delete vm")


def main():
    
    while True:
        print("Checking vms...")
        check_vms()
        print("Updating vms without ip...")
        update_vms_without_ip()
        print("Waiting...")
        time.sleep(180)


if __name__ == '__main__':
    main()
