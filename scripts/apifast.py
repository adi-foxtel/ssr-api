#!/usr/bin/env python3
"""
Web API interface for mySql API tool
"""
import asyncio
import os
import sys
sys.path.append(os.getcwd())

from datetime import datetime, timedelta

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
import json
import logging
import uvicorn
from typing import Union

from asp_clearscrambled import *
from asp_nmx_api import nmx_get_service_lists, nmx_get_service_groups

from test_nmx import *

from typing import Optional
from fastapi_utils.tasks import repeat_every

user = 'foxtel'
logging.debug('Using username %s', user)

app = FastAPI(debug=True)
app.add_middleware(PrometheusMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_route("/metrics", handle_metrics)

logger = logging.getLogger(__name__)

count = 0
onCall = False

@app.on_event("startup")
@repeat_every(seconds=30, logger=logger, wait_first=False)
def periodic():

    global count
    global onCall

    if onCall == False :
        nmx_get_harmonic_config()
    if count == 0 :
        if onCall == False :
            nmx_save_copy_harmonic_config()
    else :
        if onCall == False :
            nmx_compare_local_and_harmonic_config()
    count += 1


@app.on_event("shutdown")
def shutdown_event():
    logging.debug('shutdown_event')


@app.get("/")
def read_root():
    return {"clearscrambled_api": "v0.1"}


@app.get("/healthz")
def read_root():
    return "OK"


@app.get("/ver")
def get_versions():
    ver = "v0.3"
    return {"clearscrambled version": str(ver)}

########################          SSR API         ##################################

@app.get("/platform/manage/picture/scrambled/ssr/getdevices")
def get_devices():
    response =  nmx_get_devices()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/ssr/gettsstreams")
def get_clearscrambled():
    response =  SSR_get_streams()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/ssr/gettservicedetail/{item_id}")
def get_service_details(item_id):
    response =  SSR_get_details(item_id)
    return JSONResponse(status_code=200, content=response)

@app.post("/platform/manage/picture/scrambled/ssr/api")
async def request_post(info : Request):
    global onCall
    onCall = True

    req_info = await info.json()
    if req_info["command"] == "SCRAMBLED" or req_info["command"] == "CLEAR" or req_info["command"] == "SCRAMBLED_ARRAY" or req_info["command"] == "CLEAR_ARRAY" :
        response =  SSR_current_streams( req_info["command"], req_info["stream"], req_info["service"], req_info["state"], req_info["defaultFlag"], req_info["ServiceId"])
        onCall = False
        return JSONResponse(status_code=200, content=response)
    else :
        response =  SSR_current_streams(req_info["command"],req_info["stream"],None,None)
        onCall = False
        return JSONResponse(status_code=200, content=response)
    

########################          NMX API         ##################################

@app.get("/platform/manage/picture/scrambled/nmx/getAccessToken")
def get_nmx_token():
    response =  nmx_get_devicesaccess_token()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/nmx/getHarmonicDevices")
def get_nmx_devices():
    response = nmx_get_devices()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/nmx/getServiceList")
def get_nmx_servicelists():
    response = nmx_get_service_lists()
    return JSONResponse(status_code=200, content=response)


@app.get("/platform/manage/picture/scrambled/nmx/getServiceGroups")
def get_nmx_service_groups():
    response = nmx_get_service_groups()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/nmx/getPlanScramblingList")
def get_nmx_scrambling_lists():
    response = nmx_get_service_plans_scrambling_lists()
    return JSONResponse(status_code=200, content=response)

@app.get("/platform/manage/picture/scrambled/nmx/getRealTimeConfigChange")
def get_nmx_realtime_compare_list():
    response = nmx_compare_local_and_harmonic_config()
    return JSONResponse(status_code=200, content=response)



@app.post("/platform/manage/picture/scrambled/nmx/setClearScramble")
async def request_post(info : Request):
    req_info = await info.json()
    response =  nmx_patch_channel( req_info["Group"], req_info["ID"], req_info["status"])
    return JSONResponse(status_code=200, content=response)

@app.post("/platform/manage/picture/scrambled/nmx/synchronization")
async def synchronization_post(info : Request):
    onCall = True
    req_info = await info.json()
    response =  nmx_synchronization(req_info)
    onCall = False
    return JSONResponse(status_code=200, content=response)

serverport = int(os.getenv('MYSQL_API_PORT', 9001))

if __name__ == "__main__":
    logging.info('Starting clearscrambled API Client')
    uvicorn.run(app, host="0.0.0.0", port=serverport, log_level=10)


