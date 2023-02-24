#!/usr/bin/env python3

import sys
import json
import requests
import os
from datetime import datetime

from asp_sql_statements import getSsrServiceDetailByTsId_sql_query, getSsrScrambledTransportStream_sql_query, getNmxSsrServiceDetailByTsId_sql_query, getScrambledLocalObj_sql_query, CLRcommand_sql_query, SCRcommand_sql_query
from asp_sql_statements import Defaultcommand1_sql_query, Defaultcommand2_sql_query, CLRcommand_sql_query, SCRcommand_sql_query

from test_nmx import nmx_patch_channel

import mysql.connector as mysqlConnector
import oracledb

class InitDataClass:
    PLATFORM = os.environ['PLATFORM']

    HOST = os.environ['HOST']
    PORT = os.environ['PORT']
    DATABASE = os.environ['DATABASE']
    USER = os.environ['USER']
    PASSWORD = os.environ['PASSWORD']

    NMX = os.environ['NMX']
    NMX2 = os.environ['NMX2']
    NMX_SITE: os.environ['NMX_SITE']
    NMX2_SITE: os.environ['NMX2_SITE']
    NMX_USER = os.environ['NMX_USER']
    NMX_PASS = os.environ['NMX_PASS']

    S1 = os.environ['S1']
    S2 = os.environ['S2']
    SERVER = os.environ['SERVER']




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

    from test_nmx import nmx_get_devicesaccess_token
    ret = nmx_get_devicesaccess_token()

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

            nmxStatus = get_nmx_reference(ret, int(row[1]))

            if len(nmxStatus) == 1 : # for PTS
                o["ServiceId"] = []
                o["ServiceId"].append(nmxStatus[0]["ServiceId"])
                o["Status"] = []
                o["Status"].append(nmxStatus[0]["Status"])
            else:
                o["ServiceId"] = []
                o["ServiceId"].append(nmxStatus[0]["ServiceId"])
                o["ServiceId"].append(nmxStatus[1]["ServiceId"])
                o["Status"] = []
                o["Status"].append(nmxStatus[0]["Status"])
                o["Status"].append(nmxStatus[1]["Status"])

        else :

            if obj.NMX == obj.NMX2 :
                o["ServiceId"] = []
                o["Status"] = []
                o["ServiceId"].append("")
                o["Status"].append("")
            else:
                o["ServiceId"] = []
                o["Status"] = []
                o["ServiceId"].append("")
                o["ServiceId"].append("")
                o["Status"].append("")
                o["Status"].append("")



        if row[2] == row[0] :
            o["Phantom"] = False
        else :
            o["Phantom"] = True

        a.append(o)

    res["status"] = "ok"
    res["data"] = a
    conn.close()

    return(res)




def get_nmx_reference(ret,si_service_id):

    rezult = []

    if len(ret['rezult']) == 1 :

        if not isinstance(ret['rezult'][0], str) :

            if os.path.exists('scripts/harmonic_config' + '.json') == True :

                nmx = {}
                nmx["rezult"] = json.load(open('scripts/harmonic_config' + '.json', 'r'))

                for g in nmx["rezult"]:
                    #print(g)
                    if len(g) > 0 :
                        for s in g:
                            #print(s)
                            if s["ServiceNumber"] == si_service_id :
                                rezult.append({"ServiceId": s["ServiceId"], "Status": s["Status"]})

                rezult.append({"ServiceId": "", "Status": ""})


            else :

                rezult.append({"ServiceId": "", "Status": ""})

        else :

            rezult.append({"ServiceId": "", "Status": "offline"})

    else :

        if not isinstance(ret['rezult'][0], str) :

            if os.path.exists('scripts/harmonic_config_nmx_1' + '.json') == True :

                nmx = {}
                nmx["rezult"] = json.load(open('scripts/harmonic_config_nmx_1' + '.json', 'r'))

                found = False
                for g in nmx["rezult"]:
                    #print(g)
                    if len(g) > 0 :
                        for s in g:
                            #print(s)
                            if s["ServiceNumber"] == si_service_id :
                                found = True
                                rezult.append({"ServiceId": s["ServiceId"], "Status": s["Status"]})

                if found == False :
                    rezult.append({"ServiceId": "", "Status": ""})

            else :

                rezult.append({"ServiceId": "", "Status": ""})
        else :

            rezult.append({"ServiceId": "", "Status": "offline"})

        if not isinstance(ret['rezult'][1], str) :

            if os.path.exists('scripts/harmonic_config_nmx_2' + '.json') == True :

                nmx = {}
                nmx["rezult"] = json.load(open('scripts/harmonic_config_nmx_2' + '.json', 'r'))
                found = False
                for g in nmx["rezult"]:
                    #print(g)
                    if len(g) > 0 :
                        for s in g:
                            #print(s)
                            if s["ServiceNumber"] == si_service_id :
                                found = True
                                rezult.append({"ServiceId": s["ServiceId"], "Status": s["Status"]})

                if found == False :
                    rezult.append({"ServiceId": "", "Status": ""})

            else :

                rezult.append({"ServiceId": "", "Status": ""})
        else :

            rezult.append({"ServiceId": "", "Status": "offline"})

    return(rezult)





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

    #print(json.dumps(a, indent=4))
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
                i=0
                res["data"] = []
                nmx_response = []
                ssr_response = []
                #print(f"channelId : {channelId}")
                #print(f"ServiceId : {ServiceId}")
                for x in channelId:
                    #print("\n*** Switch to Default START\n")
                    qry = SCRcommand_sql_query

                    if(PLATFORM == "DEV") :
                        qry = qry.upper()
                        qry = qry.replace("SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1))","NULLIF(SUBSTR(NOTES,INSTR(NOTES,'(')+1,(INSTR(NOTES,')')-INSTR(NOTES,'(')-1)),'')")
                        qry = qry.replace("DEFAULT", "Default")

                    qry = qry.replace("?", str(x))
                    #print(qry)
                    cur.execute(qry)
                    conn.commit()
                    #print("\n*** Switch to Default END\n")
                    ret = f"ssr, switch {x} to Clear ok"
                    ssr_response.append(ret)
                    s = ServiceId[i]

                    if s != ["",""] and s != [""]:
                        response = nmx_patch_channel( streamId, s, "Scramble")
                        nmx_response.append(response)
                        import time
                        time.sleep(2.4)

                    i += 1

                res["data"] = [ssr_response,nmx_response]

            elif command == "CLEAR_ARRAY" :
                i=0
                res["data"] = []
                nmx_response = []
                ssr_response = []

                #print(f"channelId : {channelId}")
                #print(f"ServiceId : {ServiceId}")

                for x in channelId:
                    #print(f"\n*** {x} Switch to CLEAR\n")
                    qry = CLRcommand_sql_query

                    if(PLATFORM == "DEV") :
                        qry = qry.upper()

                    qry = qry.replace("?", str(x))
                    #print(qry)
                    cur.execute(qry)
                    conn.commit()
                    #print("\n***Switch to CLEAR END\n")
                    ret = f"ssr, switch {x} to Clear ok"
                    ssr_response.append(ret)
                    s = ServiceId[i]

                    if s != ["",""] and s != [""]:
                        response = nmx_patch_channel( streamId, s, "Clear")
                        nmx_response.append(response)
                        import time
                        time.sleep(2.4)

                    i += 1

                res["data"] = [ssr_response,nmx_response]

            elif command == "SCRAMBLED" :

                ServiceId = ServiceId[0]
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

                print(f"ServiceId: {ServiceId}")

                if ServiceId != ["",""] and ServiceId != [""]:  
                    ret = nmx_patch_channel( streamId, ServiceId, "Scramble")
                    res["data"].append(ret)

            elif command == "CLEAR" :

                ServiceId = ServiceId[0]
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

                print(f"ServiceId: {ServiceId}")

                if ServiceId != ["",""] and ServiceId != [""]:  
                    ret = nmx_patch_channel( streamId, ServiceId, "Clear")
                    res["data"].append(ret)


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
