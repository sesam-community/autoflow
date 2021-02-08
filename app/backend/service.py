from flask import Flask, request, jsonify, Response
import json
import requests
import logging
import os
import sys
from datahubs.sesam import get_all_input_pipes, create_global, get_all_pipes, get_global_pipe_config
from flask_cors import CORS, cross_origin
from sesamutils import VariablesConfig, sesam_logger
import urllib3

urllib3.disable_warnings()
app = Flask(__name__)

## Helpers
logger = sesam_logger("Steve the logger", app=app)
CORS(app,
     resources={r"/*": {
         "origins": "*"
     }},
     headers={
         'Access-Control-Request-Headers', 'Content-Type',
         'Access-Control-Allow-Origin'
     })

sesam_response = None
## Logic for running program in dev
try:
    with open("./backend/helpers.json", "r") as stream:
        logger.info("Using env vars defined in helpers.json")
        env_vars = json.load(stream)
        os.environ['sesam_jwt'] = env_vars['sesam_jwt']
        os.environ['sesam_base_url'] = env_vars['sesam_base_url']
except OSError as e:
    logger.info("Using env vars defined in SESAM")
##
    
required_env_vars = ['sesam_jwt', 'sesam_base_url']
optional_env_vars = ["Denmark_is_here"]
sesam_jwt = os.getenv('sesam_jwt')
base_url = os.getenv('sesam_base_url')

@app.route('/')
def index():
    output = {
        'service': 'Autoflow up and running',
        'remote_addr': request.remote_addr
    }
    return jsonify(output)


## Get all input pipes from SESAM to display in frontend for merging of globals.
@app.route('/get_pipes', methods=['POST'])
@cross_origin()
def get_pipes():
    return_object = []
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    datahub_config_and_tables = connectors
    pipes_in_sesam = get_all_input_pipes(
        datahub_config_and_tables['sesamJWT'],
        datahub_config_and_tables['sesamBaseURL'])

    index_value = 1
    for pipe in pipes_in_sesam:
        return_object.append({"id": index_value, "name": pipe, "groupId": 1})
        index_value = index_value + 1

    sesam_response = {"result": return_object}
    return {"pipes": pipes_in_sesam}

    
## Get all pipes from SESAM to display in frontend.
@app.route('/get_all_pipes', methods=['POST'])
@cross_origin()
def scan_sesam():
    return_object = []
    global sesam_response
    pipes_in_sesam = get_all_pipes(sesam_jwt, base_url)

    for pipe in pipes_in_sesam:
        return_object.append(pipe)
    
    return_object = sorted(return_object, key=str.swapcase)

    if len(return_object) == 0:
        tmp_pipes_for_frontend = ["It seems you have not started using SESAM yet.", "Lets run a scan of your database to get started!"]
        for pipe in tmp_pipes_for_frontend:
            return_object.append(pipe)

    sesam_response = {"result": return_object}
    return {"pipes": pipes_in_sesam}


## Get all input pipes from SESAM to display in frontend for merging of globals.
@app.route('/create_global_list', methods=['POST'])
@cross_origin()
def global_list():
    return_object = []
    response_object = None
    global sesam_response
    connectors = request.json
    pipes_to_use_for_globals = connectors['pipes']

    global_groups = [
        {
          'id': 1,
          'name': "Default List",
          'items': [],
        },
        {
          'id': 2,
          'name': "First Global",
          'items': [],
        },
        {
          'id': 3,
          'name': "Second Global",
          'items': [],
        },
        {
          'id': 4,
          'name': "Third Global",
          'items': [],
        },
        {
          'id': 5,
          'name': "Fourth Global",
          'items': [],
        },
        {
          'id': 6,
          'name': "Fifth Global",
          'items': [],
        }
    ]

    index_value = 1
    group_count = 2
    element_count = 1
    tmp_globals = []
    tmp_pipes_in_globals = []
    for pipe in pipes_to_use_for_globals:
        if "global" in pipe and pipe not in tmp_globals:
            tmp_globals.append(pipe)
            pipes_in_global = get_global_pipe_config(pipe, datahub_config_and_tables['sesamJWT'],
                      datahub_config_and_tables['sesamBaseURL'])
            tmp_pipes_in_globals.extend(pipes_in_global)
            if global_groups[element_count].get('id') == group_count:
                global_groups[element_count]['name'] = pipe
                for tmp_pipe in tmp_pipes_in_globals:
                    global_groups[element_count]['items'].append({"id": index_value, "name": tmp_pipe, "groupId": group_count})
                    index_value = index_value + 1
                element_count = element_count + 1
                group_count = group_count + 1

        else:
            if type(pipe) is dict:
                return_object.append(pipe)
            else:
                return_object.append({"id": index_value, "name": pipe, "groupId": 1})
                index_value = index_value + 1
        
        tmp_pipes_in_globals = []

    global_groups[0]['items'].extend(return_object)
    response_object = global_groups
    
    tmp_globals = []

    sesam_response = {"result": response_object}
    return {"pipes": pipes_to_use_for_globals}


## Creating globals from excisting SESAM integration
@app.route('/create_globals', methods=['POST'])
@cross_origin()
def get_globals():
    sesam_global_response = None
    global datahub_config_and_tables
    global sesam_response
    connectors = request.json
    global_selection = connectors

    selected_globals = []
    for element in global_selection['globalGroups']:
        for key, value in element.items():
            if key == "name":
                if "global-" not in value:
                    pass
                else:
                    selected_globals.append(element)

    global_name = None
    pipe_names = []
    index = 1
    for element in selected_globals:
        global_name = element['name']
        for pipe in element['items']:
            pipe_names.append(f"{pipe['name']} pip{index}")
            index = index + 1
        create_global(global_name, pipe_names,
                      datahub_config_and_tables['sesamJWT'],
                      datahub_config_and_tables['sesamBaseURL'])
        pipe_names = []
        index = 1

    sesam_response = {
        "sesam_result": "Your global pipes have been created! ;)"
    }
    return {"system_result": sesam_global_response}


## General response...
@app.route('/sesam_response', methods=['GET'])
def sesam_result():
    global sesam_response
    return sesam_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)