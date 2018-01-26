import mysql.connector
import time

def create_vm():
    # POST rancher
    # ONLY INSERT IF RANCHER RETURNS RESULT
    # INSERT INTO vms ip, rancher_id, blocked=false
    return

def delete_vm(rancher_id):
    # DELETE Request to rancher

    # ONLY DELETE FROM DB only if RANCHER RETURNS 200
    # DELETE FROM vms WHERE rancher_id = rancher_id
    return None

def create_vm_if_empty():
    # SELECT COUNT(*) FROM vms where blocked=0;
    cnx = mysql.connector.connect(user='instamakeruser', password='instabot', host='127.0.0.1', port='3307', database='instamaker')
    cursor = cnx.cursor()

    query = ("SELECT COUNT(*) FROM vms WHERE blocked=0")
    cursor.execute(query)

    for result in cursor:
        if result[0] < 1:
            create_vm()

    cursor.close()
    cnx.close()


def check_vms():
    create_vm_if_empty()
    cnx = mysql.connector.connect(user='instamakeruser', password='instabot', host='127.0.0.1', port='3307', database='instamaker')
    cursor = cnx.cursor()

    query = ("SELECT * FROM vms WHERE blocked=1")
    cursor.execute(query)

    for (ip, blocked, rancher_id, vm_name) in cursor:
        err = delete_vm(rancher_id)
        if err == None:
            create_vm()
        else:
            print("Failed to delete vm")

    cursor.close()
    cnx.close()

def main():
    while True:
        print("Checking vms")
        check_vms()
        print("Waiting")
        time.sleep(180)

if __name__ == '__main__':
    main()
