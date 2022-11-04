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
from asp_harmonic import *



#from scripts import xmppapilib, configlib
#import sleekxmpp
#import scripts.iq3 as iq3
from typing import Optional
#from scripts.iq3 import util
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


@app.on_event("startup")
async def startup_event():
    logging.debug('startup_event')


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

@app.get("/platform/manage/v1/harmonic/proswitch/realtime_status")
def get_harmonic():
    response =  harmonic_get_state()
    return JSONResponse(status_code=200, content=response)


@app.get("/platform/manage/v1/harmonic/proswitch/cached_status")
def get_harmonic():
    response =  harmonic_get_state()
    return JSONResponse(status_code=200, content=response)



@app.get("/platform/manage/v1/harmonic/proswitch/getctrlmode")
def get_harmonic():
    return {"mode":"manual"}
    response =  harmonic_get_state()

@app.put("/platform/manage/v1/harmonic/proswitch/setctrlmode")
async def post_harmonic(info : Request):
    print("put") 
    req_info = await info.json()
    print(req_info) 
    return req_info

@app.post("/harmonic/api")
async def post_harmonic(info : Request):
    req_info = await info.json()
    if req_info["command"] == "get_state":
        response =  harmonic_get_state(req_info["command"])
        return JSONResponse(status_code=200, content=response, default=str)
    elif req_info["command"] == "set_state":    
        response =  harmonic_set_state(req_info)
        return JSONResponse(status_code=200, content=response)
    elif req_info["command"] == "set_mode":    
        response =  harmonic_set_mode(req_info)
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
    req_info = await info.json()
    if req_info["command"] == "SCRAMBLED" or req_info["command"] == "CLEAR" :
        response =  SSR_current_streams(req_info["command"],req_info["service"],req_info["state"],req_info["defaultFlag"])
        return JSONResponse(status_code=200, content=response)
    else :
        response =  SSR_current_streams(req_info["command"],req_info["stream"],None,None)
        return JSONResponse(status_code=200, content=response)

@app.get("/xmpp")
def request_xmpp():
    response =  "not implemented" 
    return JSONResponse(200, response)


serverport = int(os.getenv('MYSQL_API_PORT', 9001))

if __name__ == "__main__":
    logging.info('Starting clearscrambled API Client')
    uvicorn.run(app, host="0.0.0.0", port=serverport, log_level=10)


