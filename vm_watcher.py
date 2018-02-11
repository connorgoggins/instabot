import time
import os
import requests
from requests.auth import HTTPBasicAuth

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import utils

DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1:3307")
engine = create_engine('mysql+mysqldb://instamakeruser:instabot@' +DB_HOST+'/instamaker')
Session = sessionmaker(bind=engine)

from user import User
from vm import VM


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

        vm = VM(ip=ip, rancher_id=rancher_id, blocked=False)
        session = Session()
        #if ip != '':
        session.add(vm)
        session.commit()
    return

def delete_vm(rancher_id):
    # DELETE Request to rancher
    delete_vm_url = "https://try.rancher.com/v2-beta/projects/1a1065894/hosts/"+rancher_id
    rancher_creds = utils.get_rancher_creds()
    disable_vm_url = delete_vm_url + "?action=deactivate"
    q = requests.post(
        disable_vm_url,
        auth=HTTPBasicAuth(rancher_creds["username"], rancher_creds["password"]),
    )

    if q.status_code == 200:
        r = requests.delete(
            delete_vm_url,
            auth=HTTPBasicAuth(rancher_creds["username"], rancher_creds["password"]),
        )

        if r.status_code == 200:
            # ONLY DELETE FROM DB only if RANCHER RETURNS 200
            # DELETE FROM vms WHERE rancher_id = rancher_id
            session = Session()
            session.query(VM).filter_by(rancher_id=rancher_id).delete()
            session.commit()
            return None
        else:
            return "Error deleting vm with rancher_id: "+str(rancher_id)


def update_vms_without_ip():
    session = Session()
    vms = session.query(VM).filter_by(ip="").all()
    session.commit()

    for vm in vms:
        ip, err = get_rancher_vm_ip(vm.rancher_id)
        if err == None:
            set_vm_ip(vm.rancher_id, ip)
        else:
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
    session = Session()
    count = session.query(VM).filter_by(blocked=False).count()
    session.commit()

    if count < 1:
        create_vm()

def set_vm_ip(rancher_id, ip):
    session = Session()
    if ip == None:
        ip = ""
    vm = session.query(VM).filter_by(rancher_id=rancher_id).first()
    vm.ip = ip
    session.commit()

    return

def check_vms():
    create_vm_if_empty()

    session = Session()
    vms = session.query(VM).filter_by(blocked=True).all()
    session.commit()

    for vm in vms:
        err = delete_vm(vm.rancher_id)
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
    # delete_vm("test")
    main()
