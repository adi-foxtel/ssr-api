#!/usr/bin/env python3

import sys
import json
import requests
from urllib3.exceptions import InsecureRequestWarning
import os
from datetime import datetime

import mysql.connector as mysqlConnector

class InitDataClass:
    NMX = os.environ['NMX']
    NMX_USER = os.environ['NMX_USER']
    NMX_PASS = os.environ['NMX_PASS']


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
        #print(data)
        return {"rezult": data}

    except Exception as e:
        print(e)
        return {"rezult": "error"}
        
def nmx_get_devices():
    
    ret = nmx_get_devicesaccess_token()
    if ret != 'error' :

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

            return harmonics

        except Exception as e:
            print(e)
            return {"rezult": "error"}

    return {"rezult": "error"}

def nmx_patch_channel(id,status):

    print("nmx_patch_channel")

    print(id)
    print(status)
    rezult={}

    ret = nmx_get_devicesaccess_token()
    if ret != 'error' :

        access_token = ret['rezult']['access_token']
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        url = f"https://{obj.NMX}/api/Scrambling/v2/SCG/{id}"
        print(url)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        session = requests.Session()
        session.verify = False
        
        body={"status":status}
        print(body)

        try:
           
            r = session.patch(url, json=body, headers=headers)
            data = json.loads(r.text)

            rezult = data
            print(rezult)
            return rezult

        except Exception as e:
            print(e)
            return {"rezult": "patch error"}

    
    return {"rezult": "token error"}  




def nmx_get_service_plans_scrambling_lists():
    
    ret = nmx_get_devicesaccess_token()    
    print("nmx_get_service_plans_scrambling_lists")

    if ret != 'error' :
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
                scrambling = data

                return scrambling


            except Exception as e:
                print(e)
                return {"rezult": "error"}

        except Exception as e:
            print(e)
            return {"rezult": "error"}

    return {"rezult": "error"} 




def nmx_get_service_lists():
    
    ret = nmx_get_service_lists()
    print("nmx_get_service_groups")
    
    if ret != 'error' :
        
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        ret = nmx_get_devices()

        if ret != 'error' :
            
            objectServices = []
            
            for i in ret:
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
                    return {"rezult": "error"}

        return(objectServices)

    return {"rezult": "error"} 



def nmx_get_service_groups():
    
    ret = nmx_get_devicesaccess_token()
    print("nmx_get_service_groups")

    if ret != 'error' :
        
        access_token = ret['rezult']['access_token']
        headers = {
            'Accept': "application/json",
            'Authorization': f"Bearer {access_token}"
        }

        ret = nmx_get_devices()

        if ret != 'error' :
            
            ServiceGroups = []
            ServiceGroupsSorted = [
                [] for a in range(100)
            ]
            
            for i in ret:
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
                    return {"rezult": "error"}

        plan = nmx_get_service_plans_scrambling_lists()

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






        return(ServiceGroupsSorted)

    return {"rezult": "error"} 





if __name__ == '__main__':
    nmx_get_devicesaccess_token()
