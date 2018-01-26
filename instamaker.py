#!/usr/bin/python
#Instagram Account Maker
#by Behdad Ahmadi
#Twitter: behdadahmadi
#https://github.com/behdadahmadi
#https://logicalcoders.com

# docker exec -it dc9c mysql --database=instamaker -u instamakeruser -p
# MYSQL_PASSWORD=instabot

import requests
import hmac
import hashlib
import random
import string
import json
import argparse
import socket
from faker import Faker
fake = Faker()
import mysql.connector
import ipapi
import time
import utils

def HMAC(text):
    key = '3f0a7d75e094c7385e3dbaa026877f2e067cbd1a4dbcf3867748f6b26f257117'
    hash = hmac.new(key,msg=text,digestmod=hashlib.sha256)
    return hash.hexdigest()

def randomString(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def banner():
    dotname = "-" * 31
    print " "
    print dotname.center(16,'-')
    print ".:: " + 'Instagram Account Maker' + " ::.".center(4)
    print "by Behdad Ahmadi".center(30)
    print "Twitter:behdadahmadi".center(30)
    print dotname.center(20,'-')



def create(name, username, email, password, cursor):
    params = {'name': name, 'username': username, 'email': email, 'password': password}

    getHeaders = {'User-Agent':'Instagram 7.1.1 Android (21/5.0.2; 480dpi; 1080x1776; LGE/Google; Nexus 5; hammerhead; hammerhead; en_US)',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Encoding':'gzip, deflate, sdch',
               'Accept-Language':'en-US,en;q=0.8',
               'upgrade-insecure-requests':'1'}

    s = requests.Session()
    s.get('https://instagram.com',headers=getHeaders)
    guid = randomString(8) + '-' + randomString(4) + "-" + randomString(4) + '-' + randomString(4) + '-' +randomString(12)
    device_id = 'android-' + str(HMAC(str(random.randint(1000,9999))))[0:min(64,16)]
    information = {'username':params['username'],'first_name':params['name'],'password':params['password'],'email':params['email'],'device_id':device_id,'guid':guid}
    js = json.dumps(information)
    payload = {'signed_body': HMAC(js) + '.' + js,'ig_sig_key_version':'4'}
    postHeaders = {'Host':'i.instagram.com',
                  'User-Agent':'Instagram 7.1.1 Android (21/5.0.2; 480dpi; 1080x1776; LGE/Google; Nexus 5; hammerhead; hammerhead; en_US)',
                  'Accept-Language':'en-US',
                  'Accept-Encoding':'gzip',
                  'Cookie2':'$Version=1',
                  'X-IG-Connection-Type':'WIFI',
                  'X-IG-Capabilities':'BQ=='
                  }
    x = s.post('https://i.instagram.com/api/v1/accounts/create/',headers=postHeaders,data=payload)
    result = json.loads(x.content)
    if result['status'] != 'fail':
        if result['account_created'] == True:
            print 'Account has been created successfully'

            add_user = ("INSERT INTO users (full_name, username, user_email, password) VALUES (\"%s\", \"%s\", \"%s\", \"%s\")")
            data_user = (name, username, email, password)
            cursor.execute(add_user, data_user)

        else:
            print 'Error:'
            for i in result['errors']:
                print str(result['errors'][i][0])
    else:
        if result['spam'] == True:
            print 'Instagram blocks your IP due to spamming behaviour.'

            ip = ipapi.location(None, None, "ip")

            ip = ip[2:-1]

            add_vm = ("UPDATE vms SET blocked=1 WHERE ip=\"%s\"")
            data_vm = (ip)
            cursor.execute(add_vm, data_vm)

def main():
    cnx = utils.get_db_connection()
    cursor = cnx.cursor()

    while True:
        full_name = fake.name()
        user_name = (full_name.replace(" ", "")).lower() + str(random.randint(1000,9999))
        user_email = user_name + "@gmail.com"
        pwd = "Mypassword1"
        print "Creating..."
        print full_name, user_name, user_email, pwd
        create(full_name, user_name, user_email, pwd, cursor)
        print "Sleeping..."
        time.sleep(15)

    cursor.close()
    cnx.close()

# schema
# full_name VARCHAR (50) NOT NULL, user_name VARCHAR (50) NOT NULL, user_email VARCHAR(50) NOT NULL, password VARCHAR(50) NOT NULL


if __name__ == '__main__':
    main()
