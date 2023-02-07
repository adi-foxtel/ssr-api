#!/usr/bin/env python3

import sys
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import os
from datetime import datetime

import mysql.connector as mysqlConnector


class InitDataClass:
    #NMX = os.environ['NMX']
    #NMX_USER = os.environ['NMX_USER']
    #NMX_PASS = os.environ['NMX_PASS']
    NMX="10.243.172.221"
    NMX_USER="Administrator"
    NMX_PASS="harmonic"      

obj = InitDataClass()

def nmx_get_devicesaccess_token():

    headers = {'content-type': 'application/json'}
    url = f"https://{obj.NMX}/api/Domain/v2/AccessToken"

    data = {
        "Username": obj.NMX_USER,
        "Password": obj.NMX_PASS
    }

    try:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False

        r = session.post( url, headers=headers, json=data)
        data = json.loads(r.text)

        return {"rezult": data}

    except Exception as e:
        print(e)
        return {"rezult": "nmx_get_devicesaccess_token error"}
        
def nmx_get_devices():
    
    ret = nmx_get_devicesaccess_token()

    if not isinstance(ret['rezult'], str) :

        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        url = f"https://{obj.NMX}/api/Topology/v2/Devices"
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

            return {"rezult":harmonics}

        except Exception as e:
            print(e)
            return {"rezult": "nmx_get_devices error"}

    return {"rezult": "nmx_get_devicesaccess_token error"}

def nmx_patch_channel(stream,id,status):

    print("\nnmx_patch_channel\n")
    print(f"ID {id}")
    print(f"Stream {stream}")
    print(f"Status {status}")
    rezult={}

    ret = nmx_get_devicesaccess_token()
    if not isinstance(ret['rezult'], str) :

        access_token = ret['rezult']['access_token']
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        url = f"https://{obj.NMX}/api/Scrambling/v2/SCG/{id}"

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False
        
        body={"status":status}
        print(f"URL {url} Payload {body}")

        try:
           
            r = session.patch(url, json=body, headers=headers)
            data = json.loads(r.text)
            #==================================================================
            if os.path.exists('scripts/harmonic_config_local' + '.json') == True :
                savedServiceGroups_json = json.load(open('scripts/harmonic_config_local' + '.json', 'r'))
                for g in savedServiceGroups_json:
                    if len(g) > 0 :
                        for s in g:
                            if s["ServiceId"] == id :
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
            rezult = {"rezult": data, "Group": stream }
            print(rezult)
            return rezult

        except Exception as e:
            print(e)
            return {"rezult": "nmx_patch_channel error"}

    
    return {"rezult": "nmx_get_devicesaccess_token error"}  




def nmx_get_service_plans_scrambling_lists():
    
    ret = nmx_get_devicesaccess_token()    
    print("nmx_get_service_plans_scrambling_lists")

    if not isinstance(ret['rezult'], str) :
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        url = f"https://{obj.NMX}/api/Services/v2/ServicePlans"
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False

        try:
            r = session.get( url, headers=headers)
            data = json.loads(r.text)

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

            url = f"https://{obj.NMX}/api/Scrambling/v2/SCG?ServicePlanId={ID}"

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

    return {"rezult": "nmx_get_devicesaccess_token error"} 



def nmx_get_service_lists():
    
    ret = nmx_get_devicesaccess_token()
    print("nmx_get_service_lists")
    
    if not isinstance(ret['rezult'], str) :
        
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        ret = nmx_get_devices()

        if not isinstance(ret['rezult'], str) :
            
            objectServices = []
            
            for i in ret['rezult']:
                ID = i['ID']

                url = f"https://{obj.NMX}/api/Topology/v2/Devices/{ID}/ServiceList"
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                session = requests.Session()
                session.verify = False

                try:
                    r = session.get( url, headers=headers)
                    data = json.loads(r.text)
                    services=[]

                    if len(data) > 0 :

                        for s in data:
                            services.append(s)

                        objectServices.append({"ID": ID, "services": services})

                except Exception as e:
                    print(e)
                    return {"rezult": "nmx_get_service_lists error"}

        return({"rezult": objectServices})

    return {"rezult": "nmx_get_devicesaccess_token error"} 


def nmx_compare_local_and_harmonic_config():

    res = []
    compare = []

    ret = nmx_get_devicesaccess_token()

    if isinstance(ret['rezult'], str) :
        if ret['rezult'] == "nmx_get_devicesaccess_token error" :
            res["status"] = "error"
            res["data"] = ret['NMX Server Offline']
            return(res)

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

    res["status"] = "ok"
    res["data"] = compare
    return(res)


def nmx_save_copy_harmonic_config():

    print("nmx_save_copy_harmonic_config")

    if os.path.exists('scripts/harmonic_config' + '.json') == True :

        json_data = json.load(open('scripts/harmonic_config' + '.json', 'r'))

        if os.path.exists('scripts/harmonic_config_local' + '.json') == False :

            with open('scripts/harmonic_config_local' + '.json', 'w+') as f:
                json.dump( json_data, f, indent=4, sort_keys=True)

            print("harmonic_config_local.json created")
        
        else :

            with open('scripts/harmonic_config_local' + '.json', 'w') as f:
                json.dump( json_data, f, indent=4, sort_keys=True)

            print("harmonic_config_copy.json updated")




def nmx_get_harmonic_config():
    
    print("nmx_get_harmonic_config")

    ret = nmx_get_devicesaccess_token()

    if not isinstance(ret['rezult'], str) :
        
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        ret = nmx_get_devices()

        if not isinstance(ret['rezult'], str) :
            
            ServiceGroups = []
            ServiceGroupsSorted = [
                [] for a in range(100)
            ]
            
            for i in ret['rezult']:

                ID = i['ID']
                url = f"https://{obj.NMX}/api/Topology/v2/Devices/{ID}/ServiceList"
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                session = requests.Session()
                session.verify = False

                try:
                    r = session.get( url, headers=headers)
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
                    return {"rezult": "nmx_get_service_list error"}


        ret = nmx_get_service_plans_scrambling_lists()

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
                print("harmonic_config.json updated")

            return({"rezult":ServiceGroupsSorted})

    return {"rezult": "nmx_get_service_groups error"} 




def nmx_get_service_groups():
    
    if os.path.exists('scripts/harmonic_config' + '.json') == True :
        savedServiceGroups_json = json.load(open('scripts/harmonic_config' + '.json', 'r'))
        print("harmonic_config.json read")
        return({"rezult":savedServiceGroups_json})
        #return savedServiceGroups_json

    ret = nmx_get_devicesaccess_token()
    print("nmx_get_service_groups")

    if not isinstance(ret['rezult'], str) :
        
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        ret = nmx_get_devices()

        if not isinstance(ret['rezult'], str) :
            
            ServiceGroups = []
            ServiceGroupsSorted = [
                [] for a in range(100)
            ]
            
            for i in ret['rezult']:

                ID = i['ID']
                url = f"https://{obj.NMX}/api/Topology/v2/Devices/{ID}/ServiceList"
                requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
                session = requests.Session()
                session.verify = False

                try:
                    r = session.get( url, headers=headers)
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
                    return {"rezult": "nmx_get_service_list error"}


        ret = nmx_get_service_plans_scrambling_lists()

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

            return({"rezult":ServiceGroupsSorted})

    return {"rezult": "nmx_get_service_groups error"} 


def sortByServiceNumber(k):
    return k['service']['ServiceNumber']


if __name__ == '__main__':
    nmx_get_devicesaccess_token()
