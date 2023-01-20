#!/usr/bin/env python3

import sys
import json
import requests
import os
from datetime import datetime

from asp_sql_statements import getSsrScrambledTransportStream_sql_query, getNmxSsrServiceDetailByTsId_sql_query, getScrambledLocalObj_sql_query, CLRcommand_sql_query, SCRcommand_sql_query
from asp_sql_statements import Defaultcommand1_sql_query, Defaultcommand2_sql_query, CLRcommand_sql_query, SCRcommand_sql_query

from asp_nmx_api import nmx_patch_channel

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
        o["si_service_key"] = row[2]
        o["total"] = row[3]
        o["defaults"] = row[4]
        o["clear"] = row[5]
        o["name"] = row[6]

        if row[1] != None :
            nmxStatus = get_nmx_reference(int(row[1]))
            o["ServiceId"] =  nmxStatus["ServiceId"]
            o["Status"] = nmxStatus["Status"]
        else :
            o["ServiceId"] =  ""
            o["Status"] = ""

        if row[2] == row[0] :
            o["Phantom"] = False
        else :
            o["Phantom"] = True

        a.append(o)

    res["status"] = "ok"
    res["data"] = a
    conn.close()

    return(res)

def get_nmx_reference(si_service_id):

    if os.path.exists('scripts/harmonic_config' + '.json') == True :

        nmx = {}
        nmx["rezult"] = json.load(open('scripts/harmonic_config' + '.json', 'r'))

        for g in nmx["rezult"]:
            #print(g)
            if len(g) > 0 :
                for s in g:
                    #print(s)
                    if s["ServiceNumber"] == si_service_id :
                        return {"ServiceId": s["ServiceId"], "Status": s["Status"]}

        return {"ServiceId": "", "Status": ""}
    
    else :

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

def SSR_current_streams( command, streamId, channelId, state, defaultFlag, ServiceId):

    NoneType = type(None)

    obj = InitDataClass()

    PLATFORM = obj.PLATFORM.upper()

    if type(state) == NoneType :
        if type(channelId) == NoneType :
            print(PLATFORM + " " + command )
        else :
            print(PLATFORM + " " + command + " " + str(channelId) )
    else :
        print(PLATFORM + " " + command + " " + str(channelId) )

    choices = {
        'getconfigured': getScrambledLocalObj_sql_query,
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
                i=0
                res["data"] = []
                for x in channelId:
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
                    ret = f"ssr, switch {x} to Clear ok"
                    res["data"].append(ret)
                    if ServiceId[i] != "" :
                        print("\n*** Switch to NMX Default START\n")
                        ret = nmx_patch_channel( streamId, ServiceId[i], "Scramble")
                        print(ret)
                        print("\n*** Switch to NMX Default END\n")
                        res["data"].append(ret["rezult"])
                    i += 1



            elif command == "CLEAR_ARRAY" :
                i=0
                res["data"] = []
                for x in channelId:
                    print("\n*** Switch to CLEAR\n")
                    qry = CLRcommand_sql_query

                    if(PLATFORM == "DEV") :
                        qry = qry.upper()

                    qry = qry.replace("?", str(x))
                    print(qry)
                    cur.execute(qry)
                    conn.commit()
                    print("\n***Switch to CLEAR END\n")
                    ret = f"ssr, switch {x} to Clear ok"
                    res["data"].append(ret)
                    if ServiceId[i] != "" :
                        print("\n*** Switch to NMX CLEAR START\n")
                        ret = nmx_patch_channel( streamId, ServiceId[i], "Clear")
                        print(ret)
                        print("\n*** Switch to NMX CLEAR END\n")
                        res["data"].append(ret["rezult"])
                    i += 1


            elif command == "SCRAMBLED" :

                qry = SCRcommand_sql_query
                if(PLATFORM == "DEV") :
                    qry = qry.upper()
                    qry = qry.replace("SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1))","NULLIF(SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1)),'')")
                    qry = qry.replace("DEFAULT", "Default")

                qry = qry.replace("?", str(channelId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                ret = f"ssr, switch {channelId} to Scramble ok"
                res["data"] = []
                res["data"].append(ret)

                for x in ServiceId:
                    if x != "" :
                        ret = nmx_patch_channel( streamId, x, "Scramble")
                        res["data"].append(ret["rezult"])

            elif command == "CLEAR" :

                qry = CLRcommand_sql_query

                if(PLATFORM == "DEV") :
                    qry = qry.upper()

                qry = qry.replace("?", str(channelId))
                print(qry)
                cur.execute(qry)
                conn.commit()
                ret = f"ssr, switch {channelId} to Clear ok"
                res["data"] = []
                res["data"].append(ret)

                for x in ServiceId:
                    if x != "" :
                        ret = nmx_patch_channel( streamId, x, "Clear")
                        res["data"].append(ret["rezult"])

            res["status"] = "ok"
            res["request"] = qry

    except Exception as e:

        res["status"] = "error"
        res["request"] = qry
        res["data"] = e

    finally :

       # Closing the connection
       conn.close()
       return(res)


if __name__ == '__main__':
    SSR_get_streams()
