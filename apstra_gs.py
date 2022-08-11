#!/usr/bin/python3.8
#
from aos.client import AosClient
import yaml
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AOS_IP = "1.1.1.1"
AOS_PORT = 443
AOS_USER = "admin"
AOS_PW = "xxxxxxxxxx"

aos = AosClient(protocol="https", host=AOS_IP, port=AOS_PORT)
aos.auth.login(AOS_USER, AOS_PW)

bp_name = "ENTER-FABRIC-NAME"
bp = aos.blueprint.get_id_by_name(label=bp_name)

bp_nodes = aos.blueprint.get_bp_system_nodes(bp.id)

with open(r'gslist.yaml') as file:
  generics = yaml.load(file, Loader=yaml.FullLoader)

for gsnode in generics:

    ext_rtr = aos.blueprint.create_ext_generic_systems(
        bp_id=bp.id,
        hostname=gsnode['gsname'],
    )

    node_links = list()
  
    for leafnodes in gsnode['leafports']:
     
        for nodename in bp_nodes.values():
            if nodename["hostname"] == leafnodes['lname']:
                leafid = nodename["id"]

        if gsnode['lagif'] == "lacp_active": 
            laglabel = "esilag_"+gsnode['gsname']
        else:
            laglabel = leafnodes['lname']+"_"+leafnodes['lport']

        node_links.append(
            {
                "link_group_label": laglabel,
                "lag_mode": gsnode['lagif'],
                "switch": {
                    "system_id": leafid,
                    "transformation_id": gsnode['trid'],
                    "if_name": leafnodes['lport']
                },
                "system": {"system_id": ext_rtr["id"]},
            }
        )
      
        ext_rtr_links = {"links": node_links}
        aos.blueprint.create_switch_system_links(bp.id, data=ext_rtr_links)

exit()