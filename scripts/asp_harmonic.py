#!/usr/bin/env python3

import sys 
import json 
import requests
import os
from datetime import datetime 

import mysql.connector as mysqlConnector

class InitDataClass:

    PLATFORM = os.environ['PLATFORM']
    HOST = os.environ['HOST']
    PORT = os.environ['PORT']
    DATABASE = 'harmonic'
    USER = os.environ['USER']
    PASSWORD = os.environ['PASSWORD']

def harmonic_get_state():

    NoneType = type(None)

    obj = InitDataClass()

    print("harmonic_get_state")
    print("ENVIRON VARS: " + obj.PLATFORM + " " + obj.HOST + " " + obj.PORT + " " + obj.DATABASE + " " + obj.USER + " " + obj.PASSWORD )

    a = []
    res = {}

    qry = "select json_extract(json_data, '$.data') from site_status"

    PLATFORM = obj.PLATFORM.upper()

    #qry = qry.upper()

    if(PLATFORM == "DEV") :
        print(qry)

    # Creating connection with the MySQL Server Running 
    conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)
    
    # Creating a cursor object to traverse the resultset
    cur = conn.cursor(prepared=True)
    cur.execute(qry)

    for row in cur:
        res["data"] = json.loads(row[0].replace("OPTUS", "OPTUS10"))

    conn.close()
    print(res)
    return(res)



def harmonic_set_mode(payload):
    NoneType = type(None)

    obj = InitDataClass()

    print("harmonic_set_mode")
    print(obj.PLATFORM + " " + json.dumps(payload) )
    print("ENVIRON VARS: " + obj.PLATFORM + " " + obj.HOST + " " + obj.PORT + " " + obj.DATABASE + " " + obj.USER + " " + obj.PASSWORD )

    a = []
    res = {}

    qry = "not implemented"

    PLATFORM = obj.PLATFORM.upper()

    if(PLATFORM == "DEV") :
        print(qry)
        qry = qry.replace("NVL", "coalesce")

    # Creating connection with the MySQL Server Running 
    conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)
    
    # Creating a cursor object to traverse the resultset
    #cur = conn.cursor(prepared=True)
    #cur.execute(qry)

    #for row in cur:
    #    o = {}
    #    o["time"] = str(row[0])
    #    o["json"]  = json.loads(row[1])
    #
    #    a.append(o)

    res["status"] = "ok"
    res["info"] = qry
    res["data"] = a

    conn.close()
    print(res)
    return(res)



def harmonic_set_state(payload):
    NoneType = type(None)

    obj = InitDataClass()

    print("harmonic_set_state")
    print(obj.PLATFORM + " " + json.dumps(payload) )
    print("ENVIRON VARS: " + obj.PLATFORM + " " + obj.HOST + " " + obj.PORT + " " + obj.DATABASE + " " + obj.USER + " " + obj.PASSWORD )

    a = []
    res = {}

    qry = "not implemented"

    PLATFORM = obj.PLATFORM.upper()

    if(PLATFORM == "DEV") :
        print(qry)
        qry = qry.replace("NVL", "coalesce")

    # Creating connection with the MySQL Server Running 
    conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)
    
    # Creating a cursor object to traverse the resultset
    #cur = conn.cursor(prepared=True)
    #cur.execute(qry)

    #for row in cur:
    #    o = {}
    #    o["time"] = str(row[0])
    #    o["json"]  = json.loads(row[1])
    #
    #    a.append(o)

    res["status"] = "ok"
    res["info"] = qry
    res["data"] = a

    conn.close()
    print(res)
    return(res)


if __name__ == '__main__':
    harmonic_get_state(sys.argv[1])
    
