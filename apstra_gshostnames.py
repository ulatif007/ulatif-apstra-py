#!/usr/bin/python3.8
#
# <*******************## Copyright 2023 Juniper Networks, Inc. All rights reserved.# Licensed under the Juniper Networks Script Software License (the "License").# You may not use this script file except in compliance with the License, which is located at# http://www.juniper.net/support/legal/scriptlicense/# Unless required by applicable law or otherwise agreed to in writing by the parties, software# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.## *******************>
#
from aos.client import AosClient
import urllib3
import requests
import csv
import json
import time
import sys
from getpass import getpass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# IP of AOS Server
username = 'admin'

print('############################################################################')
print('This script shall save all GS hostnames in an output file')
print('Written in Python using APSTRA 4.1.2 REST API\n')
print('(c) 2023 Juniper Networks Professional Services')
print('Author: Usman Latif\n')
print('\nDisclaimer:')
print('\nNote: This script is only provded for once off deployment purposes')
print('Juniper or Authors donot commit to supporting this script on ongoing basis')
print('############################################################################\n')
input('\nPress ENTER to continue ...\n')

aos_server = input('\nEnter AOS server IP = ')

print('Enter admin password')
pass_word = getpass()

bp_name = input('\nEnter blueprint name = ')

csvfilename = input('\nEnter CSV Filename = ')


# authenticate and get a auth token
url = 'https://' + aos_server + '/api/user/login'
headers = { 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
data = '{ \"username\":\"' + username + '\", \"password\":\"' + pass_word + '\" }'
response = requests.request("POST", url, data=data, headers=headers, verify=False)
auth_token = response.json()['token']
print('\n Auth Token Obtained\n')
print('-------------------------------------------------------------')

# get BP information
url = 'https://' + aos_server + '/api/blueprints'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request('GET', url, headers=headers, verify=False)

for bpitem,bplist in response.json().items():
   for bpdict in bplist:
     if bpdict.get('label')==bp_name:
       print('The BP ID for '+ bp_name + 'is : '+bpdict.get('id'))
       bpuuid = bpdict.get('id')

print('\n BP info obtained \n')
print('-------------------------------------------------------------')

# Get all node hostname info for GS nodes
url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/nodes?node_type=system'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request('GET', url, data=data, headers=headers, verify=False)
all_nodes = response.json()

gsnames_data = {}
print('\n node DB obtained\n')

with open('nodes.csv','w') as f:

   with open(csvfilename, 'r') as readobj:
      csvreader = csv.DictReader(readobj)
    
      for row in csvreader:
         srvrname = row.get('server_label')

         writer = csv.writer(f)
         for nodeitem,nodekvp in all_nodes.items():
            for nodekey,nodeval in nodekvp.items():
               if nodeval.get('role')=='generic':
                 if nodeval.get('label')==srvrname:
                   row_data=[nodeval.get('label'),nodeval.get('hostname')]
                   writer.writerow(row_data)

exit()
