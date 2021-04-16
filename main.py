#!/usr/bin/env python3

"""
entrada: ciudad, telefono
salida: temperatura
consultar pronostico clima, si supera 20 enviar sms con alerta

https://api.openweathermap.org/data/2.5/weather?q=Lima&appid=1857efc0aad350431e9002ed71d9395d&units=metric
"""

import requests
import json
from bottle import route, run, template, response, hook
import os
import boto3
#from twilio.rest import Client

_allow_origin = '*'
_allow_methods = 'PUT, GET, POST, DELETE, OPTIONS'
_allow_headers = 'Authorization, Origin, Accept, Content-Type, X-Requested-With'

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = _allow_origin
    response.headers['Access-Control-Allow-Methods'] = _allow_methods
    response.headers['Access-Control-Allow-Headers'] = _allow_headers

@route('/api/v1/<ciudad>/<telefono>')
def index(ciudad="", telefono=""):
    response.content_type = 'application/json'
    if ciudad=="" or telefono=="":
        return json.dumps({'status': 'error', 'msg': 'Deber poner una ciudad y telefono'})

    request_url = "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=MYTOKEN&units=metric" % ciudad
    #print("url: ", request_url)
    status = ''

    #try:
    clima = requests.get(request_url)
    temp_min = 0
    temp_max = 0
    if clima.status_code==200:
        status = 'ok'
        #print(clima.content)
        #print(clima.text)
        obj_json = clima.json()
        temp_min = obj_json['main']['temp_min']
        temp_max = obj_json['main']['temp_max']
        

        if temp_max > 20:
            client = boto3.client(
                "sns",
                region_name="us-east-1",
                aws_access_key_id='KEY',
                aws_secret_access_key='ACCESS'
            )

            # Send your sms message.
            client.publish(
                PhoneNumber="+51"+str(telefono),
                Message="Alerta! En %s se supera los 20C" % ciudad
            )
            # Twilio da error de formato de numero, por eso lo comente
            """
            account_sid = 'sadsadsadsa'
            auth_token = 'ssss'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
                                 body="Mensaje demo.",
                                 from_='+51966296636',
                                 to='+51' + str(telefono)
                             )

            print(message.sid)
            """
    else:
        status = 'error'
        temp_min = 0
        temp_max = 0
    return json.dumps({'status': status, 'msg': {'temperatura': temp_max}})
    #except:
    #    return json.dumps({'status': 'error', 'msg': 'Ocurrio un error, vuelva a intentar'})
    

run(host='localhost', port=8080, debug=True)
