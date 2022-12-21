#!/usr/bin/env python3

import sys
import json
import requests
import os
from datetime import datetime

from asp_sql_statements import getSsrServiceDetailByTsId_sql_query, getSsrScrambledTransportStream_sql_query, getNmxSsrServiceDetailByTsId_sql_query, getScrambledLocalObj_sql_query, CLRcommand_sql_query, SCRcommand_sql_query
from asp_sql_statements import Defaultcommand1_sql_query, Defaultcommand2_sql_query, CLRcommand_sql_query, SCRcommand_sql_query

from getServiceGroups import getServiceGroups_json

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

    #qry = getSsrServiceDetailByTsId_sql_query
    qry = getNmxSsrServiceDetailByTsId_sql_query

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
        o["si_service_id"] = row[1]
        o["total"] = row[2]
        o["defaults"] = row[3]
        o["clear"] = row[4]
        o["name"] = row[5]

        if row[1] != None :
            nmxStatus = get_nmx_reference(int(row[1]))
            o["ServiceId"] =  nmxStatus["ServiceId"]
            o["Status"] = nmxStatus["Status"]
        else :
            o["ServiceId"] =  ""
            o["Status"] = ""

        a.append(o)

    res["status"] = "ok"
    res["data"] = a
    conn.close()
    return(res)

def get_nmx_reference(si_service_id):

    nmx = getServiceGroups_json

    for g in nmx["rezult"]:
        if len(g) > 0 :
            for s in g:
                if s["ServiceNumber"] == si_service_id :
                    return {"ServiceId": s["ServiceId"], "Status": s["Status"]}
    return {"ServiceId": "", "Status": ""}


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

    print(json.dumps(a, indent=4))
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
        'SCRAMBLED': SCRcommand_sql_query,
        'CLEAR_ARRAY': CLRcommand_sql_query,
        'SCRAMBLED_ARRAY': SCRcommand_sql_query

    }

    qry = choices.get(command, 'default')

    a = []
    res = {}

    try:

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

        if type(state) != NoneType :

            if command == "SCRAMBLED_ARRAY" :
                for x in streamId:
                    print("\n*** Switch to Default START\n")
                    qry = SCRcommand_sql_query

                    if(PLATFORM == "DEV") :
                        qry = qry.upper()
                        qry = qry.replace("SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1))","NULLIF(SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1)),'')")
                        qry = qry.replace("DEFAULT", "Default")

                    qry = qry.replace("?", str(x))
                    print(qry)
                    cur.execute(qry)
                    conn.commit()
                    print("\n*** Switch to Default END\n")

            elif command == "CLEAR_ARRAY" :
                for x in streamId:
                    print("\n*** Switch to CLEAR\n")
                    qry = CLRcommand_sql_query

                    if(PLATFORM == "DEV") :
                        qry = qry.upper()

                    qry = qry.replace("?", str(x))
                    print(qry)
                    cur.execute(qry)
                    conn.commit()
                    print("\n***Switch to CLEAR END\n")

            elif command == "SCRAMBLED" :

                print("\n*** Switch to Default START\n")
                qry = SCRcommand_sql_query
                if(PLATFORM == "DEV") :
                    qry = qry.upper()
                    qry = qry.replace("SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1))","NULLIF(SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1)),'')")
                    qry = qry.replace("DEFAULT", "Default")

                qry = qry.replace("?", str(streamId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                print("\n*** Switch to Default END\n")

            elif command == "CLEAR" :

                print("\n*** Switch to CLEAR\n")
                qry = CLRcommand_sql_query

                if(PLATFORM == "DEV") :
                    qry = qry.upper()

                qry = qry.replace("?", str(streamId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                print("\n***Switch to CLEAR END\n")

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
