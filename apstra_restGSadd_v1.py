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
from getpass import getpass
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# IP of AOS Server
username = 'admin'

print('############################################################################')
print('Bulk GS creation and CT assignment')
print('Written in Python using APSTRA 4.1.2 REST API\n')
print('(c) 2023 Juniper Networks Professional Services')
print('Author: Usman Latif\n')
print('Acknowledgements:')
print('   - Koral Ozgunay')
print('   - Shabbir Ahmed')
print('\nDisclaimer:')
print('\nNote: This script is only provded for once off deployment purposes')
print('Juniper or Authors donot commit to supporting this script on ongoing basis')
print('############################################################################\n')
input('\nPress ENTER to continue ...\n')

aos_server = input('\nEnter AOS server IP = ')

print('Enter admin password')
pass_word = getpass()

CSV_Filename = input('\nEnter CSV Filename = ')
bp_name = input('\nEnter blueprint name = ')


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

# read CSV file and parse UUID for leaf info
url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/nodes?node_type=system'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request('GET', url, data=data, headers=headers, verify=False)
node_dict = response.json()

print('\n node DB obtained\n')
print(node_dict)
print('-------------------------------------------------------------')
print('\nCSV File row iteration\n')

with open(CSV_Filename, 'r') as read_obj:
   csv_reader = csv.DictReader(read_obj)

   for row in csv_reader:
     print(row)
     print('\n')
     srvr_name = row.get('server_label')
     srvr_hname = row.get('server_hostname')
     srvr_port1 = row.get('srv_intf1')
     srvr_port2 = row.get('srv_intf2')
     leaf1_hname = row.get('leaf1_name')
     leaf2_hname = row.get('leaf2_name')
     leaf1_port = row.get('leaf1_srv_intf')
     leaf2_port = row.get('leaf2_srv_intf')
     lag_mode = row.get('lacp_mode')
     leaf_type = row.get('leaf_model')
     vn_list = row.get('ct_name').split("|")
     logical_device = { "id": "AOS-10x1G-10x10G-10x25G", "display_name": "AOS-10x1G-10x10G-10x25G", "panels": [{ "port_groups": [{ "count": 2, "speed": { "value": 10, "unit": "G"},"roles": ["leaf", "access"]}], "port_indexing": { "order": "T-B, L-R", "start_index": 1, "schema": "absolute" }, "panel_layout": { "row_count": 1, "column_count": 2 } }] }

     for nodeitem,nodekvp in node_dict.items():
       for nodekey,nodeval in nodekvp.items():
         if nodeval.get('hostname')==leaf1_hname:
           leaf1_uuid = nodeval.get('id')
           print(leaf1_hname)
           print(leaf1_uuid)
         elif nodeval.get('hostname')==leaf2_hname:
           leaf2_uuid = nodeval.get('id')
           print(leaf2_hname)
           print(leaf2_uuid)

     print("----------------------------------------------------------")

     if leaf1_port.startswith('et-') and leaf_type=='q5120':
       leaf1_trid=1
     elif leaf1_port.startswith('xe-') and leaf_type=='q5120':
       leaf1_trid=2
     elif leaf1_port.startswith('ge-') and leaf_type=='q5120':
       leaf1_trid=3
     elif leaf1_port.startswith('xe-') and leaf_type=='q10008':
       leaf1_trid=1
     elif leaf1_port.startswith('ge') and leaf_type=='q10008':
       leaf1_trid=2

     if leaf2_port.startswith('et-') and leaf_type=='q5120':
       leaf2_trid=1
     elif leaf2_port.startswith('xe-') and leaf_type=='q5120':
       leaf2_trid=2
     elif leaf2_port.startswith('ge-') and leaf_type=='q5120':
       leaf2_trid=3
     elif leaf2_port.startswith('xe-') and leaf_type=='q10008':
       leaf2_trid=1
     elif leaf2_port.startswith('ge') and leaf_type=='q10008':
       leaf2_trid=2


     if lag_mode=='none' and leaf2_hname=='none':
        links = [{
                    "lag_mode": None,
                    "tags": [],
                    "switch": {
                      "system_id": leaf1_uuid,
                      "transformation_id": leaf1_trid,
                      "if_name": leaf1_port
                    },
                    "system": {
                      "system_id": None,
                    }
                 }];


     elif lag_mode=='none' and leaf2_hname!='none':
        links = [{
                    "lag_mode": None,
                    "tags": [],
                    "switch": {
                      "system_id": leaf1_uuid,
                      "transformation_id": leaf1_trid,
                      "if_name": leaf1_port
                    },
                    "system": {
                      "system_id": None,
                    }
                 },
                 {
                     "lag_mode": None,
                     "tags": [],
                     "switch": {
                       "system_id": leaf2_uuid,
                       "transformation_id": leaf2_trid,
                       "if_name": leaf2_port
                  },
                    "system": {
                      "system_id": None,
                    }
                 }];


     elif lag_mode!='none':
        links = [{
                    "lag_mode": lag_mode,
                    "tags": [],
                    "switch": {
                      "system_id": leaf1_uuid,
                      "transformation_id": leaf1_trid,
                      "if_name": leaf1_port
                    },
                    "system": {
                      "system_id": None,
                    }
                 },
		 {
                     "lag_mode": lag_mode,
                     "tags": [],
                     "switch": {
                       "system_id": leaf2_uuid,
                       "transformation_id": leaf2_trid,
                       "if_name": leaf2_port
                  },
                    "system": {
                      "system_id": None,
                    }
                 }];

     body = {
       "links": links,
       "new_systems": [
         {
          "system_group_label": srvr_name,
          "label": srvr_name,
          "hostname": srvr_hname,
          "system_type": "server",
          "tags": [],
          "logical_device": logical_device,
          "port_channel_id_min": 0,
          "port_channel_id_max": 0
         }
       ]
     };
     obj = json.dumps(body)
     headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
     url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/switch-system-links?async=full'
     response = requests.request("POST", url, data=obj, headers=headers, verify=False)

# Form LAG interfaces for interfaces with LACP 
     lag_details = '{"links":{"'+str(leaf1_hname)+'<->'+str(srvr_name)+'(link-000000001)[1]":{"group_label":"link1","lag_mode":"'+str(lag_mode)+'"},"'+str(leaf2_hname)+'<->'+str(srvr_name)+'(link-000000002)[1]":{"group_label":"link1","lag_mode":"'+str(lag_mode)+'"}}}'


     headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
     url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/leaf-server-link-labels'
     response = requests.request("PATCH", url, data=lag_details, headers=headers, verify=False)

print('\nGS definition and Leaf links have been staged\n')
print('\nStandby 15 seconds before starting CT assignment ...\n')

time.sleep(15)

# Find cabling info and assign CT

with open('GS_addition_v01.csv', 'r') as read_obj:
   csv_reader = csv.DictReader(read_obj)

   for row in csv_reader:
     print("\n--------------------------------------------------------")
     print(row)
     print("--------------------------------------------------------")
     srvr_name = row.get('server_label')
     srvr_port1 = row.get('srv_intf1')
     srvr_port2 = row.get('srv_intf2')
     leaf1_hname = row.get('leaf1_name')
     leaf2_hname = row.get('leaf2_name')
     leaf1_port = row.get('leaf1_srv_intf')
     leaf2_port = row.get('leaf2_srv_intf')
     lag_mode = row.get('lacp_mode')
     leaf_type = row.get('leaf_model')
     ct_list = row.get('ct_name').split("|")

# Obtaining CM from running blueprint

     url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/experience/web/cabling-map?type=staging&comment=cabling-map&aggregate_links=true'
     headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
     response = requests.request("GET", url, headers=headers, verify=False)
     
     print('\n########### Finding INTF Data ############')    

     intfdata = []
     leafhname = []
     leafport = []
     i=0
     print('lag_mode <> leaf2_hname : ' + lag_mode + ' <> ' + leaf2_hname)
     if lag_mode=='none' and leaf2_hname=='none':
       for listdict in response.json().get('links'):
          if listdict.get('role')=='to_generic':
            if listdict.get('endpoints')[0]['system']['label']==leaf1_hname and listdict.get('endpoints')[0]['interface']['if_name']==leaf1_port:
              print(listdict.get('endpoints')[0]['system']['label'])
              print(listdict.get('endpoints')[0]['interface']['if_name'])
              intfdata.append(listdict.get('endpoints')[0]['interface']['id'])

     elif lag_mode=='none' and leaf2_hname!='none':
       i=0
       leafhname.append(leaf1_hname)
       leafport.append(leaf1_port)
       leafhname.append(leaf2_hname)
       leafport.append(leaf2_port)

       while i<2:
         for listdict in response.json().get('links'):
            if listdict.get('endpoints')[0]['system']['label']==leafhname[i] and listdict.get('endpoints')[0]['interface']['if_name']==leafport[i]:
              print(listdict.get('endpoints')[0]['system']['label'])
              print(listdict.get('endpoints')[0]['interface']['if_name'])
              intfdata.append(listdict.get('endpoints')[0]['interface']['id'])
         i += 1

     elif lag_mode!='none':
         for listdict in response.json().get('links'):
            if listdict.get('role')=='to_generic':
              if listdict.get('endpoints')[0]['system']['label']==leaf1_hname and listdict.get('endpoints')[0]['interface']['if_name']==leaf1_port:
                print(listdict.get('endpoints')[1]['system']['label'])
                gs_system_id = listdict.get('endpoints')[1]['system']['id']

                for lstdict in response.json().get('links'):
                   if lstdict.get('role')=='to_generic' and lstdict.get('type')=='aggregate_link':
                     if lstdict.get('endpoints')[0]['system']['id']==gs_system_id:
                       print('Found LAG: ' + lstdict.get('endpoints')[0]['system']['label'])
                       intfdata.append(lstdict.get('endpoints')[1]['interface']['id'])


     print('############## Final CT INTF IDs ###################') 
     print('intfdata\n')
     print(intfdata)
     print('\n')
     print('############## Assigning CT to INTFs ###############')

# Obtaining CT information from running BP

     url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/endpoint-policies'
     headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
     response = requests.request("GET", url, headers=headers, verify=False)
     ctpolicies = response.json()

     for ct_name in ct_list:
        for listdict in ctpolicies.get('endpoint_policies'):
           if listdict.get('label')==ct_name and listdict.get('policy_type_name')=='batch':
             print(listdict.get('label'))
             print(listdict.get('id'))
             ct_id = listdict.get('id')
             for ct_intf in intfdata:
                ct_details = {"application_points": [{"id": ct_intf, "policies": [{ "policy": ct_id, "used": True}]}]}
                url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/obj-policy-batch-apply?async=full'
                headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
                response = requests.request("PATCH", url, data=json.dumps(ct_details), headers=headers, verify=False)
                print(response.text)

exit()
