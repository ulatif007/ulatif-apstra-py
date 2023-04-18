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
print('Bulk GS deletion')
print('Written in Python using APSTRA 4.1.2 REST API\n')
print('(c) 2023 Juniper Networks Professional Services')
print('Author: Usman Latif\n')
print('Acknowledgements:')
print('   - Koral Ozgunay')
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

url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/nodes?node_type=system'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request('GET', url, data=data, headers=headers, verify=False)
node_dict = response.json()
response.close()

url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/experience/web/cabling-map?type=staging&comment=cabling-map&aggregate_links=true'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request("GET", url, headers=headers, verify=False)
cm_dict = response.json()
response.close()

url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/endpoint-policies'
headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
response = requests.request("GET", url, headers=headers, verify=False)
ctpolicies = response.json()
response.close()

print('\n node DB obtained\n')
print('-------------------------------------------------------------')
print('\nCSV File row iteration\n')

row_num=1
task_check=20
with open(CSV_Filename, 'r') as read_obj:
   csv_reader = csv.DictReader(read_obj)

   for row in csv_reader:
     print('\n')
     print('##############-#############-###############')
     print('row number = ',row_num)
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
     ct_list = row.get('ct_name').split("|")

     for nodeitem,nodekvp in node_dict.items():
       for nodekey,nodeval in nodekvp.items():
         if nodeval.get('label')==srvr_name:
           egs_uuid = nodeval.get('id')


# Processing CM

     intfdata = []
     intfuuid = []
     leafhname = []
     leafport = []
     policylist = []
     app_points = []
     i=0
     process_data='yes'

     if lag_mode=='none' and leaf2_hname=='none':
       for listdict in cm_dict.get('links'):
          if listdict.get('role')=='to_generic':
            if listdict.get('endpoints')[0]['system']['label']==leaf1_hname and listdict.get('endpoints')[1]['system']['label']==srvr_name:
              intfdata.append(listdict.get('id'))
            if listdict.get('endpoints')[0]['system']['label']==leaf1_hname and listdict.get('endpoints')[0]['interface']['if_name']==leaf1_port:
              intfuuid.append(listdict.get('endpoints')[0]['interface']['id'])

     elif lag_mode=='none' and leaf2_hname!='none':
       i=0
       leafhname.append(leaf1_hname)
       leafport.append(leaf1_port)
       leafhname.append(leaf2_hname)
       leafport.append(leaf2_port)

       print(leafhname)

       while i<2:
         for listdict in cm_dict.get('links'):
            if listdict.get('role')=='to_generic':
              if listdict.get('endpoints')[0]['system']['label']==leafhname[i] and listdict.get('endpoints')[1]['system']['label']==srvr_name:
                intfdata.append(listdict.get('id'))
              if listdict.get('endpoints')[0]['system']['label']==leafhname[i] and listdict.get('endpoints')[0]['interface']['if_name']==leafport[i]:
                intfuuid.append(listdict.get('endpoints')[0]['interface']['id'])
         i += 1

     else:
       process_data='no'

     if process_data=='yes':
       print('--- Final INTF IDs and CT ---') 
       print('intfdata\n')
       print(intfdata)

       i=0
       for ct_name in ct_list:
          for listdict in ctpolicies.get('endpoint_policies'):
             if listdict.get('label')==ct_name and listdict.get('policy_type_name')=='batch':
               print(listdict.get('label'))
               print(listdict.get('id'))
               ctdata = {"policy":listdict.get('id'),"used":False}
          policylist.append(ctdata)
          i += 1

       i=0
       for all_intf in intfuuid:
          app_data = {"id":all_intf,"policies":policylist}
          app_points.append(app_data)
          i += 1

       headers = { 'AuthToken':auth_token, 'Content-Type':"application/json", 'Cache-Control':"no-cache" }
       url = 'https://' + aos_server + '/api/blueprints/' + bpuuid + '/batch?comment=batch-api'

       obj = {"operations":[{"path":"/obj-policy-batch-apply","method":"PATCH","payload":{"application_points":app_points}},{"path":"/delete-switch-system-links","method":"POST","payload":{"link_ids":intfdata}},{"path":"/external-generic-systems/"+egs_uuid,"method":"DELETE","payload":None}]}

       response = requests.request("POST", url, data=(json.dumps(obj)), headers=headers, verify=False)
       print(response.status_code)
       print(response.text)
       response.close()

       time.sleep(5)

     row_num += 1
     task_check -= 1
     if task_check==0:
       input('\nCheck Task List in Apstra and press ENTER if pending tasks are 0')
       task_check=20

print('\n\nE-GS have been deleted. E-GS with LAG may be deleted manually')
exit()
