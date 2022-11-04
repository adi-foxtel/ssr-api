#!/usr/bin/env python3

import sys 
import json 
import requests
import os
from datetime import datetime 

from asp_sql_statements import getSsrServiceDetailByTsId_sql_query, getSsrScrambledTransportStream_sql_query, getScrambledLocalObj_sql_query, CLRcommand_sql_query, SCRcommand_sql_query
from asp_sql_statements import Defaultcommand1_sql_query, Defaultcommand2_sql_query, CLRcommand_sql_query, SCRcommand_sql_query

import mysql.connector as mysqlConnector
import oracledb

class InitDataClass:
    PLATFORM = os.environ['PLATFORM']
    HOST = os.environ['HOST']
    PORT = os.environ['PORT']
    DATABASE = os.environ['DATABASE']
    USER = os.environ['USER']
    PASSWORD = os.environ['PASSWORD']



def SSR_get_details(streamId):

    NoneType = type(None)
    obj = InitDataClass()

    a = []
    res = {}

    qry = getSsrServiceDetailByTsId_sql_query

    PLATFORM = obj.PLATFORM.upper()

    streamId = int(streamId)
    qry = qry.replace("?", str(streamId))

    if PLATFORM == "DEV" :
        qry = qry.upper()
        qry = qry.replace("NVL", "coalesce")
        conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)
    else :
        dsn_tns = obj.HOST + "/" + obj.DATABASE
        conn = oracledb.connect(user=obj.USER, password=obj.PASSWORD, dsn=dsn_tns)

    # Creating a cursor object to traverse the resultset
    cur = conn.cursor()
    cur.execute(qry)

    for row in cur:
        o = {}
        o["stream"] = streamId
        o["source_chan_id"] = row[0]
        o["total"] = row[1]
        o["defaults"] = row[2]
        o["clear"] = row[3]
        o["name"] = row[4]

        a.append(o)

    res["status"] = "ok"
    res["data"] = a

    conn.close()
    print(qry)
    print(res)
    return(res)

    

def SSR_get_streams():

    NoneType = type(None)
    obj = InitDataClass()

    a = []
    res = {}

    qry = getSsrScrambledTransportStream_sql_query

    PLATFORM = obj.PLATFORM.upper()

    if PLATFORM == "DEV" :
        qry = qry.upper()
        qry = qry.replace("NVL", "coalesce")
        conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)
    else:
        # Creating connection with the Oracle Server Running
        dsn_tns = obj.HOST + "/" + obj.DATABASE
        conn = oracledb.connect(user=obj.USER, password=obj.PASSWORD, dsn=dsn_tns)

    # Creating a cursor object to traverse the resultset
    cur = conn.cursor()
    cur.execute(qry)

    for row in cur:
        o = {}
        o["out_stream_id"] = row[0]
        o["total"] = row[1]
        o["defaults"] = row[2]
        o["altered"] = row[3]
        o["clear"] = row[4]

        a.append(o)

    res["status"] = "ok"
    res["data"] = a

    conn.close()

    print(qry)
    print(res)
    return(res)

def SSR_current_streams(command,streamId,state,defaultFlag):
    
    NoneType = type(None)

    obj = InitDataClass()

    PLATFORM = obj.PLATFORM.upper()

    if type(state) == NoneType :
        if type(streamId) == NoneType :
            print(PLATFORM + " " + command )
        else :    
            print(PLATFORM + " " + command + " " + str(streamId) )
    else :
        print(PLATFORM + " " + command + " " + str(streamId) + " " + state + " " + str(defaultFlag) )
    
    choices = {
        'getconfigured': getScrambledLocalObj_sql_query,
        'gettservicedetail': getSsrServiceDetailByTsId_sql_query, 
        'gettsstreams': getSsrScrambledTransportStream_sql_query,
        'CLEAR': CLRcommand_sql_query,
        'SCRAMBLED': SCRcommand_sql_query
    }
    
    qry = choices.get(command, 'default')

    a = []
    res = {}

    try:

        if type(streamId) != NoneType :
            streamId = int(streamId)
            qry = qry.replace("?", str(streamId))
     
        if PLATFORM == "DEV" :
            qry = qry.upper()
            qry = qry.replace("NVL", "coalesce")
            conn = mysqlConnector.connect(host=obj.HOST, port=obj.PORT, database=obj.DATABASE, user=obj.USER, password=obj.PASSWORD)

        else:
            # Creating connection with the Oracle Server Running
            dsn_tns = obj.HOST + "/" + obj.DATABASE
            conn = oracledb.connect(user=obj.USER, password=obj.PASSWORD, dsn=dsn_tns)
        
        # Creating a cursor object to traverse the resultset
        cur = conn.cursor()

        if type(state) == NoneType :

            print("mySql GET request")
            cur.execute(qry)

            for row in cur:
                o = {}
                if command == "gettsstreams" :
                    o["out_stream_id"] = row[0]
                    o["total"] = row[1]
                    o["defaults"] = row[2]
                    o["altered"] = row[3]
                    o["clear"] = row[4]
                else:
                    o["source_chan_id"] = row[0]
                    o["total"] = row[1]
                    o["defaults"] = row[2]
                    o["clear"] = row[3]
                    o["name"] = row[4]
                a.append(o)

        else :

            if command == "SCRAMBLED" :

                #if defaultFlag == True :
                #    print("DEFAULT")
                #    qry = Defaultcommand1_sql_query

                #    if(PLATFORM == "DEV") :
                #        qry = qry.upper()
                #        qry = qry.replace("DEFAULT", "Default")
                #        qry = qry.replace("'Default ECM_KEY_NUM = ('|| ECM_KEY_NUM || ')'","CONCAT('Default ECM_KEY_NUM = (', CAST(ECM_KEY_NUM AS CHAR), ')')")

                #    qry = qry.replace("?", str(streamId))
                #    print(qry)
                #    cur.execute(qry)
                #    conn.commit()
                #    print("DEFAULT END")

                print("SCRAMBLED")
                qry = SCRcommand_sql_query
                if(PLATFORM == "DEV") :
                    qry = qry.upper()
                    qry = qry.replace("SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1))","NULLIF(SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1)),'')")
                    qry = qry.replace("DEFAULT", "Default")
    
                qry = qry.replace("?", str(streamId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                print("SCRAMBLED END")

            elif command == "CLEAR" :
                print("CLEAR")
                qry = CLRcommand_sql_query

                if(PLATFORM == "DEV") :
                    qry = qry.upper()

                qry = qry.replace("?", str(streamId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                print("CLEAR END")
                
                #if defaultFlag == True :
                #    print("DEFAULT")
                #    qry = Defaultcommand2_sql_query

                #    if(PLATFORM == "DEV") :
                #        qry = qry.upper()
                #        qry = qry.replace("DEFAULT", "Default") 
    
                #    qry = qry.replace("?", str(streamId))
                #    print(qry)
                #    cur.execute(qry)
                #    conn.commit()
                #    print("DEFAULT END")
                #else :
                #    print("DEFAULT FLAG NOT RECOGNIZED")
                    
            o = {}
            a.append(o)
            res["data"].push(a)

    except Exception as e:

        res["status"].push("error") 
        res["request"].push(qry) 
        res["data"].push(e)

    finally :

       # Closing the connection
       conn.close()
       return(res)


if __name__ == '__main__':
    SSR_get_streams()
    #SSR_current_streams(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])

