import http.client
import json
import sys
import os
from base64 import b64encode

import parameters

def getAuthToken(controller_ip, username, password):
    conn = http.client.HTTPSConnection(controller_ip)
    authstring = username + ":" + password
    userandpass = b64encode(authstring.encode("ascii")).decode("ascii")
    authstring = 'Basic %s' % userandpass

    headers = {
        'content-type': "application/json",
        'authorization': authstring
    }

    conn.request("POST", "/api/system/v1/auth/token", headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data['Token']

def getApiCall(controller_ip, uri, token ):
    conn = http.client.HTTPSConnection(controller_ip)

    headers = {
        'x-auth-token': token
    }

    conn.request("GET", uri, headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data

def getAccessData(model, ethernetport, neighbor):
    with open('database.json') as f:
        data = json.load(f)
        print(data)

    output = {} ##Create a variable to build the dictionary

    for item in data:
        if(item["neighbor-name"] == neighbor):
            output["site"] = item["site"]
            for interfaces in item["interfaceIndex"]:
                if(interfaces["portIndex"] == ethernetport):
                     output["mgmt_vlan"]= interfaces["mgmt_vlan"]
                     output["mgmt_vlan_ipv4"]= interfaces["mgmt_vlan_ipv4"]
                     output["data_vlan"]= interfaces["data_vlan"]
                     output["voice_vlan"]= interfaces["voice_vlan"]
                     output["hostname"]= interfaces["hostname"]
            for templates in item["portTemplates"]:
                if(templates["model"] == model):
                     output["template"] = templates["template"]
            output["default_router"] = item["default_router"]
    return output

def postApiCall(controller_ip, uri, token, postdata ):
    conn = http.client.HTTPSConnection(controller_ip)

    headers = {
        'content-type': "application/json",
        'x-auth-token': token
    }

    conn.request("POST", uri, postdata, headers=headers)

    res = conn.getresponse()
    data = json.loads(res.read().decode("utf-8"))
    return data

def generateClaimToSiteJSON(parameters, deviceId, configId, siteId):
    tmp_data = '{'
    tmp_data += '"siteId":"' + siteId + '",'
    tmp_data += '"deviceId":"' + deviceId + '",'
    tmp_data += '"type":"Default",'
    tmp_data += '"imageInfo":{'
    tmp_data += '"imageId":"",'
    tmp_data += '"skip":true'
    tmp_data += '},'
    tmp_data += '"configInfo":{'
    tmp_data += '"configId":"' + configId + '",'
    tmp_data += '"configParameters":[' 
    tmp_data += '{"key":"hostname","value":"' + parameters["hostname"] + '"},'
    tmp_data += '{"key":"data_vlan","value":"' + str(parameters["data_vlan"]) + '"},'
    tmp_data += '{"key":"mgmt_vlan_ipv4","value":"' + parameters["mgmt_vlan_ipv4"] + '"},'
    tmp_data += '{"key":"default_router","value":"' + parameters["default_router"] + '"},'
    tmp_data += '{"key":"voice_vlan","value":"' + str(parameters["voice_vlan"]) + '"},'
    tmp_data += '{"key":"mgmt_vlan","value":"' + str(parameters["mgmt_vlan"]) + '"}'
    tmp_data += ']'  ##configParameters Closing
    tmp_data += '}' ##configInfo Closing
    tmp_data += '}'  ##end of JSON
    return tmp_data