import os
import mysql.connector
def get_db_connection():
    DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    cnx = mysql.connector.connect(user='instamakeruser', password='instabot', host=DB_HOST, port='3307', database='instamaker')
    return cnx

def get_rancher_creds():
	return {"username": "84A8FF6B1431E5594C4C", "password": "YY3bJko3mNdpGQG4GfAYiXqgGWymCFPcWTuHfDU9"}