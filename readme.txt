=====================================
Creation of External Generic Systems
Using Apstra Python API

Dated: Aug/2022

(c) 2022 Usman Latif
Juniper Networks
Professional Services
=====================================


Python 3.8 is recommended
And venv is preferred

Packages needed:

> apstra-api-python
> urllib3
> pyyaml


(venv3) bash-3.2$ python --version
Python 3.8.2

(venv3) bash-3.2$ 

The script requires user to input details of generic systems using a YAML input file = gslist.yaml


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

Following lag modes are supported in the API call:
"lag_mode": "static_lag"
"lag_mode": "lacp_active"
"lag_mode": "lacp_passive"
"lag_mode": null 

However, the script only accepts two forms of lag_mode in the YAML:

lag_mode: lacp_active
lag_mode: null

Transformation ID (trid) can be noted down from the device profiles section of the UI


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


Reference output for nested dictionary that provides information about all blueprint nodes

Note: In the script, the variable bp_nodes returns a list of dictionaries from the running blueprint
A snapshot of the returned list of dictionaries is shown below for reference:

{'Aw2CARtrd-kh3s7warE': 
{'port_channel_id_max': None, 'tags': None, 'system_type': 'switch', 'deploy_mode': None, 
'id': 'Aw2CARtrd-kh3s7warE', 
'port_channel_id_min': None, 
'position_data': {'position': 0, 'pod': 0, 'plane': 0, 'region': 0}, 
'property_set': None, 
'hostname': 'ECC3DCDSP1', 
'group_label': None, 
'label': 'ECC3DCDSP1', 
'role': 'spine', 
'management_level': 'full_control', 
'system_id': None, 
'type': 'system', 
'external': False
}, 
'aBjoeiyMztM9lXKFeHc': <.....repeats...> }



