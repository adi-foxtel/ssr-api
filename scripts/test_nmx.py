#!/usr/bin/env python3

import sys
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import os
from datetime import datetime

import mysql.connector as mysqlConnector

class InitDataClass:

#    PLATFORM = os.environ['PLATFORM']
#    NMX = os.environ['NMX']
#    NMX2 = os.environ['NMX2']
#    NMX_SITE: os.environ['NMX_SITE']
#    NMX2_SITE: os.environ['NMX2_SITE']
#    NMX_USER = os.environ['NMX_USER']
#    NMX_PASS = os.environ['NMX_PASS']
#    S1 = os.environ['S1']
#    S2 = os.environ['S2']
#    SERVER = os.environ['SERVER']

    PLATFORM = "NPD"
    NMX = "10.243.172.221"
    NMX2 = "10.243.172.221"
    NMX_SITE = "PTS"
    NMX2_SITE = "PTS"
    NMX_USER = "Administrator"
    NMX_PASS = "harmonic"
    S1 = "10.197.12.25"
    S2 = "10.197.12.89"
    SERVER = "10.197.12.25"

obj = InitDataClass()

def nmx_get_devicesaccess_token():

    headers = {'content-type': 'application/json'}

    data = {
        "Username": obj.NMX_USER,
        "Password": obj.NMX_PASS
    }

    if obj.NMX == obj.NMX2 :

        rezult = []

        url = f"https://{obj.NMX}/api/Domain/v2/AccessToken"

        try:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            r = session.post( url, headers=headers, json=data)
            data = json.loads(r.text)
            rezult.append(data)

        except Exception as e:
            print(e)
            rezult.append(f"nmx_get_devicesaccess_token {obj.NMX_SITE} error")

        return {"rezult": rezult}

    else :

        data1 = None
        data2 = None
        rezult = []

        url = f"https://{obj.NMX}/api/Domain/v2/AccessToken"

        try:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            r = session.post( url, headers=headers, json=data)
            data1 = json.loads(r.text)
            rezult.append(data1)

        except Exception as e:
            print(e)
            rezult.append("nmx_get_devicesaccess_token {obj.NMX_SITE} error")

        url = f"https://{obj.NMX2}/api/Domain/v2/AccessToken"

        try:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            r = session.post( url, headers=headers, json=data)
            data2 = json.loads(r.text)
            rezult.append(data2)

        except Exception as e:
            print(e)
            rezult.append(f"nmx_get_devicesaccess_token {obj.NMX2_SITE} error")

        return {"rezult": rezult}



def nmx_get_devices(nmx,ret):

    if len(ret) == 1 :

        access_token = ret[0]
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        url = f"https://{nmx}/api/Topology/v2/Devices"
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False

        try:
            r = session.get( url, headers=headers)
            data = json.loads(r.text)

            harmonics=[]

            for i in data:
                if 'HardwareCategory' in i['DeviceInfo']:
                    if i['DeviceInfo']['HardwareCategory'] == "Harmonic":
                        harmonics.append({"ID": i['DeviceInfo']['ID'], "Name": i['DeviceInfo']['Name']})
                else:
                    continue

            return {"rezult": [harmonics]}

        except Exception as e:
            print(e)
            return {"rezult": "nmx_get_devices error"}

    else :

        headers = [
            {
                'Accept': "application/json",
                'Authorization': f"Bearer {ret[0]}"
            },
            {
                'Accept': "application/json",
                'Authorization': f"Bearer {ret[1]}"
            }
        ]

        harmonics1=[]
        harmonics2=[]
        rezult = []

        if ret[0] != 'nmx_get_devicesaccess_token error' :

            url = f"https://{obj.NMX}/api/Topology/v2/Devices"
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            try:
                r = session.get( url, headers=headers[0])
                data = json.loads(r.text)


                for i in data:
                    if 'HardwareCategory' in i['DeviceInfo']:
                        if i['DeviceInfo']['HardwareCategory'] == "Harmonic":
                            harmonics1.append({"ID": i['DeviceInfo']['ID'], "Name": i['DeviceInfo']['Name']})
                    else:
                        continue

                rezult.append(harmonics1)

            except Exception as e:
                print(e)
                rezult.append("nmx_1_get_devices error")

        else :
            print('nmx_1_get_devicesaccess_token error')
            rezult.append("nmx_1_get_devicesaccess_token error")

        if ret[1] != 'nmx_get_devicesaccess_token error' :

            url = f"https://{obj.NMX2}/api/Topology/v2/Devices"
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            try:
                r = session.get( url, headers=headers[1])
                data = json.loads(r.text)


                for i in data:
                    if 'HardwareCategory' in i['DeviceInfo']:
                        if i['DeviceInfo']['HardwareCategory'] == "Harmonic":
                            harmonics2.append({"ID": i['DeviceInfo']['ID'], "Name": i['DeviceInfo']['Name']})
                    else:
                        continue

                rezult.append(harmonics2)

            except Exception as e:
                print(e)
                rezult.append("nmx_2_get_devices error")
        else :
            print("nmx_2_get_devicesaccess_token error")
            rezult.append("nmx_2_get_devicesaccess_token error")


        return {"rezult": rezult}


def nmx_save_copy_harmonic_config():

    print("nmx_save_copy_harmonic_config")

    ret = nmx_get_devicesaccess_token()

    if len(ret['rezult']) == 1 :

        if not isinstance(ret['rezult'][0], str) :

            if os.path.exists('scripts/harmonic_config' + '.json') == True :

                json_data = json.load(open('scripts/harmonic_config' + '.json', 'r'))

                if os.path.exists('scripts/harmonic_config_local' + '.json') == False :

                    with open('scripts/harmonic_config_local' + '.json', 'w+') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_local.json created")

                else :

                    with open('scripts/harmonic_config_local' + '.json', 'w') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_local.json updated")
    else :

        if not isinstance(ret['rezult'][0], str) :

            if os.path.exists('scripts/harmonic_config_nmx_1' + '.json') == True :

                json_data = json.load(open('scripts/harmonic_config_nmx_1' + '.json', 'r'))

                if os.path.exists('scripts/harmonic_config_nmx_1_local' + '.json') == False :

                    with open('scripts/harmonic_config_nmx_1_local' + '.json', 'w+') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_nmx_1_local.json created")

                else :

                    with open('scripts/harmonic_config_nmx_1_local' + '.json', 'w') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_nmx_1_local.json updated")

            if os.path.exists('scripts/harmonic_config_nmx_2' + '.json') == True :

                json_data = json.load(open('scripts/harmonic_config_nmx_2' + '.json', 'r'))

                if os.path.exists('scripts/harmonic_config_nmx_2_local' + '.json') == False :

                    with open('scripts/harmonic_config_nmx_2_local' + '.json', 'w+') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_nmx_2_local.json created")

                else :

                    with open('scripts/harmonic_config_nmx_2_local' + '.json', 'w') as f:
                        json.dump( json_data, f, indent=4, sort_keys=True)

                    print("harmonic_config_nmx_2_local.json updated")




def nmx_compare_local_and_harmonic_config():

    res = []
    compare = []

    ret = nmx_get_devicesaccess_token()
    rezult = []

    if len(ret["rezult"]) == 2 :

        if isinstance(ret['rezult'][0], str) :

            if ret['rezult'][0] == "nmx_get_devicesaccess_token error" :
                rezult.append({"status":"error","data":f'NMX {obj.NMX_SITE} Server Offline'})

        else:
            json_harmonic = json.load(open('scripts/harmonic_config_nmx_1' + '.json', 'r'))
            json_local = json.load(open('scripts/harmonic_config_nmx_1_local' + '.json', 'r'))

            if json_harmonic != json_local :

                for b in json_harmonic:
                    if len(b) > 0 :
                        for r in b :

                            for a in json_local:
                                if len(a) > 0 :
                                    for p in a :

                                        if p["ServiceId"] == r["ServiceId"] and p["Status"] != r["Status"] :
                                            compare.append(r)

            rezult.append({"status":"ok","data":compare})

        if isinstance(ret['rezult'][1], str) :

            if ret['rezult'][1] == "nmx_get_devicesaccess_token error" :
                rezult.append({"status":"error","data":f'NMX {obj.NMX2_SITE} Server Offline'})

        else:
            json_harmonic = json.load(open('scripts/harmonic_config_nmx_2' + '.json', 'r'))
            json_local = json.load(open('scripts/harmonic_config_nmx_2_local' + '.json', 'r'))

            if json_harmonic != json_local :

                for b in json_harmonic:
                    if len(b) > 0 :
                        for r in b :

                            for a in json_local:
                                if len(a) > 0 :
                                    for p in a :

                                        if p["ServiceId"] == r["ServiceId"] and p["Status"] != r["Status"] :
                                            compare.append(r)

            rezult.append({"status":"ok","data":compare})

    else :

        if isinstance(ret['rezult'][0], str) :

            if ret['rezult'][0] == "nmx_get_devicesaccess_token error" :
                rezult.append({"status":"error","data":'NMX PTS Server Offline'})
        else:
            json_harmonic = json.load(open('scripts/harmonic_config' + '.json', 'r'))
            json_local = json.load(open('scripts/harmonic_config_local' + '.json', 'r'))

            if json_harmonic != json_local :

                for b in json_harmonic:
                    if len(b) > 0 :
                        for r in b :

                            for a in json_local:
                                if len(a) > 0 :
                                    for p in a :

                                        if p["ServiceId"] == r["ServiceId"] and p["Status"] != r["Status"] :
                                            compare.append(r)

            rezult.append({"status":"ok","data":compare})

    print(rezult)
    return(rezult)




def nmx_get_harmonic_config():

    from datetime import datetime
    time = str(datetime.now())
    print(f"{time} nmx_get_harmonic_config")

    ret = nmx_get_devicesaccess_token()

    if len(ret['rezult']) == 1 :
        print("1 server")
        if not isinstance(ret['rezult'][0], str) :

            access_token = [ret['rezult'][0]['access_token']]
            headers = {
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token[0]}"
            }

            ret = nmx_get_devices(obj.NMX,access_token)

            if not isinstance(ret['rezult'], str) :

                ServiceGroups = getServiceGroups(obj.NMX,headers,ret["rezult"][0])
                ServiceGroupsSorted = [
                    [] for a in range(100)
                ]

                ret = nmx_get_service_plans_scrambling_lists(obj.NMX,headers)

                if isinstance(ret['rezult'], str) :
                    return {"rezult": ret['rezult']}

                ServiceGroups.sort(key=sortByServiceNumber)

                if not isinstance(ret['rezult'], str) :

                    plan = ret['rezult']

                    for i in ServiceGroups :

                        for p in plan:
                            if p['Name'] == str(i['service']['ServiceNumber']) :

                                tag = p['Name']
                                tag_service = tag[-3:]
                                tag_group   = tag[:len(tag) - 3]
                                i['service']['Channel'] = int(tag_service)
                                i['service']['Group'] = int(tag_group)
                                i['service']['Status'] = p['Status']
                                i['service']['ServiceId'] = p['ID']

                                ServiceGroupsSorted[int(i['group'])].append(i['service'])

                    if os.path.exists('scripts/harmonic_config' + '.json') == False :
                        with open('scripts/harmonic_config' + '.json', 'w+') as f:
                            json.dump( ServiceGroupsSorted, f, indent=4, sort_keys=True)
                        print("harmonic_config.json created")

                    else :
                        with open('scripts/harmonic_config' + '.json', 'w') as f:
                            json.dump(ServiceGroupsSorted, f, indent=4, sort_keys=True)
                        time = str(datetime.now())
                        print(f"{time} harmonic_config.json updated")

                    return({"rezult":"harmonic_config updated"})

    else :
        print("2 servers")
        access_token = []
        if not isinstance(ret['rezult'][0], str) :
            access_token.append(ret['rezult'][0]['access_token'])
        else :
            access_token.append(ret['rezult'][0])

        if not isinstance(ret['rezult'][1], str) :
            access_token.append(ret['rezult'][1]['access_token'])
        else :
            access_token.append(ret['rezult'][1])

        ret = nmx_get_devices(obj.NMX,access_token)

        headers = [
            {
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token[0]}"
            },
            {
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token[1]}"
            }
        ]

        if not isinstance(ret['rezult'][0], str) :

            ServiceGroups1 = getServiceGroups(obj.NMX,headers[0],ret["rezult"][0])
            ServiceGroupsSorted1 = [
                [] for a in range(100)
            ]

            ret1 = nmx_get_service_plans_scrambling_lists(obj.NMX,headers[0])

            if isinstance(ret1['rezult'], str) :
                return {"rezult": ret1['rezult']}

            ServiceGroups1.sort(key=sortByServiceNumber)

            if not isinstance(ret1['rezult'], str) :

                plan = ret1['rezult']

                for i in ServiceGroups1 :

                    for p in plan:
                        if p['Name'] == str(i['service']['ServiceNumber']) :

                            tag = p['Name']
                            tag_service = tag[-3:]
                            tag_group   = tag[:len(tag) - 3]
                            i['service']['Channel'] = int(tag_service)
                            i['service']['Group'] = int(tag_group)
                            i['service']['Status'] = p['Status']
                            i['service']['ServiceId'] = p['ID']

                            ServiceGroupsSorted1[int(i['group'])].append(i['service'])

                if os.path.exists('scripts/harmonic_config_nmx_1' + '.json') == False :
                    with open('scripts/harmonic_config_nmx_1' + '.json', 'w+') as f:
                        json.dump( ServiceGroupsSorted1, f, indent=4, sort_keys=True)
                    print("harmonic_config_nmx_1.json created")

                else :
                    with open('scripts/harmonic_config_nmx_1' + '.json', 'w') as f:
                        json.dump(ServiceGroupsSorted1, f, indent=4, sort_keys=True)
                    time = str(datetime.now())
                    print(f"{time} harmonic_config_nmx_1.json updated")

                #return({"rezult":"harmonic_config_nmx_1.json updated"})

        if not isinstance(ret['rezult'][1], str) :

            ServiceGroups2 = getServiceGroups(obj.NMX2,headers[1],ret["rezult"][1])
            ServiceGroupsSorted2 = [
                [] for a in range(100)
            ]

            ret2 = nmx_get_service_plans_scrambling_lists(obj.NMX2,headers[1])
            if isinstance(ret2['rezult'], str) :
                return {"rezult": ret2['rezult']}

            ServiceGroups2.sort(key=sortByServiceNumber)

            if not isinstance(ret2['rezult'], str) :

                plan = ret2['rezult']

                for i in ServiceGroups2 :

                    for p in plan:
                        if p['Name'] == str(i['service']['ServiceNumber']) :

                            tag = p['Name']
                            tag_service = tag[-3:]
                            tag_group   = tag[:len(tag) - 3]
                            i['service']['Channel'] = int(tag_service)
                            i['service']['Group'] = int(tag_group)
                            i['service']['Status'] = p['Status']
                            i['service']['ServiceId'] = p['ID']

                            ServiceGroupsSorted2[int(i['group'])].append(i['service'])

                if os.path.exists('scripts/harmonic_config_nmx_2' + '.json') == False :
                    with open('scripts/harmonic_config_nmx_2' + '.json', 'w+') as f:
                        json.dump( ServiceGroupsSorted2, f, indent=4, sort_keys=True)
                    print("harmonic_config_nmx_2.json created")

                else :
                    with open('scripts/harmonic_config_nmx_2' + '.json', 'w') as f:
                        json.dump(ServiceGroupsSorted2, f, indent=4, sort_keys=True)
                    time = str(datetime.now())
                    print(f"{time} harmonic_config_nmx_2.json updated")

    return {"rezult": "nmx_get_service_groups error"}


def getServiceGroups(nmx,header,devices) :

    ServiceGroups = []

    for i in devices:

        ID = i['ID']
        url = f"https://{nmx}/api/Topology/v2/Devices/{ID}/ServiceList"
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False

        try:
            r = session.get( url, headers=header)
            data = json.loads(r.text)

            if len(data) > 0 :

                for s in data:
                    tag = str(s["ServiceNumber"])
                    if len(tag) > 3 :
                        tag_service = tag[-3:]
                        tag_group   = tag[:len(tag) - 3]
                        ServiceGroups.append({"group": int(tag_group), "service": s})

        except Exception as e:
            print(e)
            return {"rezult": "ServiceList error"}

    return ServiceGroups


def nmx_get_service_plans_scrambling_lists(nmx,headers):

    url = f"https://{nmx}/api/Services/v2/ServicePlans"
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    session = requests.Session()
    session.verify = False

    try:
        r = session.get( url, headers=headers)
        data = json.loads(r.text)

        if "Message" in data :
            print(data["Message"])
            return {"rezult": data["Message"] }

        scrambling=[]

        ID = 'undefined'
        active = False
        for i in data:
            if 'Active' in i:
                if i['Active'] == True:
                    ID = i['ID']
                    active = True
            else:
                continue

        url = f"https://{nmx}/api/Scrambling/v2/SCG?ServicePlanId={ID}"

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False

        try:
            r = session.get( url, headers=headers)

            data = json.loads(r.text)
            scrambling = {"rezult": data}

            return scrambling


        except Exception as e:
            print(e)
            return {"rezult": "nmx_get_service_plans_scrambling_list error"}

    except Exception as e:
        print(e)
        return {"rezult": "nmx_get_service_plans error"}


def sync_the_other_server(data):

    headers = {
        'Content-Type': "application/json",
        'Accept': "application/json"
    }

    PORT = 9001

    if obj.SERVER == obj.S1 :
        url = f"http://{obj.S2}:{PORT}/platform/manage/picture/scrambled/nmx/synchronization"
    else :
        url = f"http://{obj.S1}:{PORT}/platform/manage/picture/scrambled/nmx/synchronization"

    print(url)

    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    session = requests.Session()
    session.verify = False

    try:
        r = session.post(url, json=data, headers=headers)
        data = json.loads(r.text)
        rezult = {"rezult": data }
        print(rezult)
        return rezult

    except Exception as e:
        print(e)
        return {"rezult": "sync_the_other_server error"}


def nmx_synchronization(data) :

    ret = nmx_get_devicesaccess_token()

    if len(ret['rezult']) == 1 :

        try:
            with open('scripts/harmonic_config_local' + '.json', 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config_local.json")

            with open('scripts/harmonic_config' + '.json', 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config.json")

            return {"rezult": "ok"}

        except Exception as e:
            print(e)
            return {"rezult": "nmx_synchronization error"}

    else :

        try:
            with open('scripts/harmonic_config_nmx_1_local' + '.json', 'w') as f:
                json.dump( data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config_nmx_1_local.json")

            with open('scripts/harmonic_config_nmx_1' + '.json', 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config_nmx_1.json")

            with open('scripts/harmonic_config_nmx_2_local' + '.json', 'w') as f:
                json.dump( data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config_nmx_2_local.json")

            with open('scripts/harmonic_config_nmx_2' + '.json', 'w') as f:
                json.dump(data, f, indent=4, sort_keys=True)
                print("Patch change from other server saved in harmonic_config_nmx_2.json")

        except Exception as e:
            print(e)
            return {"rezult": "nmx_synchronization error"}



def nmx_patch_channel(stream,id,status):

    print("\nnmx_patch_channel\n")
    print(f"ID {id}")
    print(f"Stream {stream}")
    print(f"Status {status}")
    rezult = []
    savedServiceGroups_json = None

    ret = nmx_get_devicesaccess_token()

    if len(ret['rezult']) == 1 :

        if not isinstance(ret['rezult'][0], str) :

            access_token = ret['rezult'][0]['access_token']
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token}"
            }

            url = f"https://{obj.NMX}/api/Scrambling/v2/SCG/{id[0]}"

            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            body={"status":status}
            print(f"URL {url} Payload {body}")

            try:

                r = session.patch(url, json=body, headers=headers)
                data = json.loads(r.text)

                print(data)
                #==================================================================
                if os.path.exists('scripts/harmonic_config_local' + '.json') == True :
                    savedServiceGroups_json = json.load(open('scripts/harmonic_config_local' + '.json', 'r'))
                    for g in savedServiceGroups_json:
                        if len(g) > 0 :
                            for s in g:
                                if s["ServiceId"] == id[0] :
                                    sto = s["Status"]
                                    s["Status"] = status
                                    stn = s["Status"]
                                    print(f"oldStatus {sto} newStatus {stn}")

                    with open('scripts/harmonic_config_local' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config_local.json")

                    with open('scripts/harmonic_config' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config.json")
                #==================================================================
                rezult.append({"ServiceId": id[0], "rezult": data, "Group": stream })

            except Exception as e:
                print(e)
                rezult.append({"rezult": "nmx_patch_channel error" })

        else :
            print(e)
            rezult.append({"rezult": ret['rezult'][0] })

    else :

        if not isinstance(ret['rezult'][0], str) :

            access_token = ret['rezult'][0]['access_token']
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token}"
            }

            url = f"https://{obj.NMX}/api/Scrambling/v2/SCG/{id[0]}"

            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            body={"status":status}
            print(f"URL {url} Payload {body}")

            try:

                r = session.patch(url, json=body, headers=headers)
                data = json.loads(r.text)
                #==================================================================
                if os.path.exists('scripts/harmonic_config_nmx_1_local' + '.json') == True :
                    savedServiceGroups_json = json.load(open('scripts/harmonic_config_nmx_1_local' + '.json', 'r'))
                    for g in savedServiceGroups_json:
                        if len(g) > 0 :
                            for s in g:
                                if s["ServiceId"] == id[0] :
                                    sto = s["Status"]
                                    s["Status"] = status
                                    stn = s["Status"]
                                    print(f"oldStatus {sto} newStatus {stn}")

                    with open('scripts/harmonic_config_nmx_1_local' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config_nmx_1_local.json")

                    with open('scripts/harmonic_config_nmx_1' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config_nmx_1.json")

                #==================================================================
                rezult.append({"ServiceId": id[0], "rezult": data, "Group": stream })

            except Exception as e:
                print(e)
                rezult.append({"rezult": f"nmx_patch_channel {obj.NMX_SITE} error" })

        else :
            print(e)
            rezult.append({"rezult": ret['rezult'][0] })

        import time
        time.sleep(2.4)

        if not isinstance(ret['rezult'][1], str) :

            access_token = ret['rezult'][1]['access_token']
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json",
                'Authorization': f"Bearer {access_token}"
            }

            url = f"https://{obj.NMX2}/api/Scrambling/v2/SCG/{id[1]}"

            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
            session = requests.Session()
            session.verify = False

            body={"status":status}
            print(f"URL {url} Payload {body}")

            try:

                r = session.patch(url, json=body, headers=headers)
                data = json.loads(r.text)
                #==================================================================
                if os.path.exists('scripts/harmonic_config_nmx_2_local' + '.json') == True :
                    savedServiceGroups_json = json.load(open('scripts/harmonic_config_nmx_2_local' + '.json', 'r'))
                    for g in savedServiceGroups_json:
                        if len(g) > 0 :
                            for s in g:
                                if s["ServiceId"] == id[1] :
                                    sto = s["Status"]
                                    s["Status"] = status
                                    stn = s["Status"]
                                    print(f"oldStatus {sto} newStatus {stn}")

                    with open('scripts/harmonic_config_nmx_2_local' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config_nmx_2_local.json")

                    with open('scripts/harmonic_config_nmx_2' + '.json', 'w') as f:
                        json.dump(savedServiceGroups_json, f, indent=4, sort_keys=True)
                        print("Patch change saved in harmonic_config_nmx_2.json")
                #==================================================================
                rezult.append({"ServiceId": id[1], "rezult": data, "Group": stream })

            except Exception as e:
                print(e)
                rezult.append({"rezult": f"nmx_patch_channel {obj.NMX2_SITE} error" })

        else :
            print(e)
            rezult.append({"rezult": ret['rezult'][1] })

    print(f"nmx_patch_channel returns: {rezult}")
    sync_the_other_server(savedServiceGroups_json)
    return(rezult)



def sortByServiceNumber(k):
    return k['service']['ServiceNumber']




if __name__ == '__main__':
    nmx_get_harmonic_config()



