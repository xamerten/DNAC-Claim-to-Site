import http.client
import json
import sys
import os
import time
from base64 import b64encode
from pprint import pprint


import parameters
import functions

DNAC_USER = parameters.DNA_CENTER['username']
DNAC_PASSWORD = parameters.DNA_CENTER['password']
DNAC_HOST = parameters.DNA_CENTER['host']

## Get Auth Token from DNAC API
token = functions.getAuthToken(DNAC_HOST, DNAC_USER, DNAC_PASSWORD)
print("----- DNAC Access Token -----")
print(token)
## GET List of Unclaimed devices
## use first found device
uri = "/dna/intent/api/v1/onboarding/pnp-device/?state=Unclaimed"

print("----- Unclaimed PnP Devices -----")
unclaimed = functions.getApiCall(DNAC_HOST, uri, token)

print(unclaimed)

for item in unclaimed:
   print(item["id"] + "  -  " + item["deviceInfo"]["pid"] + "  -  " + item["deviceInfo"]["neighborLinks"][0]["remoteDeviceName"] + "  -  " + item["deviceInfo"]["neighborLinks"][0]["remoteInterfaceName"])

print("----- First Unclaimed Device -----")
unclaimedDeviceId = unclaimed[0]["id"]
unclaimedDeviceModel = unclaimed[0]["deviceInfo"]["pid"]
unclaimedDeviceRemoteHostname = unclaimed[0]["deviceInfo"]["neighborLinks"][0]["remoteDeviceName"]
unclaimedDeviceRemoteInterface = unclaimed[0]["deviceInfo"]["neighborLinks"][0]["remoteInterfaceName"]
print("Unclaimed Deviec ID: \r\n  --> " + unclaimedDeviceId)

print("----- getAccessData -----")
claimdetails = functions.getAccessData("C9300-48P", "GigabitEthernet0/1/1", "P1S5-4k-Fus-G")

pprint(claimdetails) ## for demo output

print("----- Collect Site ID -----")
epochtime = int(round(time.time()*1000))

uri = "/dna/intent/api/v1/site-health?timestamp=" + str(epochtime)
print(uri)
sites = functions.getApiCall(DNAC_HOST, uri, token)
siteId = ""

for site in sites["response"]:
    if site["siteName"] == claimdetails["site"]:
        siteId = site["siteId"]

print(siteId)

print("----- Collect Template ID -----")

uri = "/dna/intent/api/v1/template-programmer/project?name=Onboarding%20Configuration"
templates = functions.getApiCall(DNAC_HOST, uri, token)

pprint(templates) ## for demo output

for item in templates: ##find the template ID in DNAC
    for templatelist in item["templates"]:
        if(templatelist["name"] == claimdetails["template"]):
            templateId = templatelist["id"]

print("----- Template ID -----")
print("Found matching template ID for " + claimdetails["template"] + " : \r\n  --> " + templateId)

##final claiming
##build post data

tmp_configParameters = []

for key, value in claimdetails.items():
    tmp_dict = {}
    tmp_dict["key"] = key
    tmp_dict["value"] = value
    tmp_configParameters.append(tmp_dict)

tmp_configlist = dict()
tmp_configlist["configId"] = templateId
tmp_configlist["configList"] = tmp_configParameters

tmp_deviceclaimlist = dict()
tmp_deviceclaimlist["deviceClaimList"] = tmp_configlist
tmp_deviceclaimlist["deviceId"] = unclaimedDeviceId

print("----1\r\n")
print(json.dumps(tmp_configlist, indent=1))
print("----2\r\n")
print(json.dumps(tmp_configParameters))
print("----3\r\n")
print(json.dumps(tmp_deviceclaimlist, indent=1))
print("------------------\r\n")

##claim to Site API
print("------Function----\r\n")
cdata = functions.generateClaimToSiteJSON(claimdetails, unclaimedDeviceId, templateId, siteId)
print(cdata)

##posting a claim
uri = "/dna/intent/api/v1/onboarding/pnp-device/site-claim"

claimresult = functions.postApiCall(DNAC_HOST, uri, token, cdata)
pprint(claimresult)
