from flask import Flask, request, jsonify, Response
import json
import requests
import logging
import os
import sys
from datahubs.sesam import get_all_input_pipes, create_global_with_equality, update_global_with_equality, create_global, update_global, get_all_pipes, get_global_pipe_config
from statics.global_list import global_group_list
from flask_cors import CORS, cross_origin
from sesamutils import VariablesConfig, sesam_logger
import urllib3
from itertools import zip_longest

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
global_pipes_config = []
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
        tmp_pipes_for_frontend = ["It seems like your Sesam instance is empty"]
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
    global global_pipes_config
    connectors = request.json
    pipes_to_use_for_globals = connectors['pipes']
    list_of_global_pipes_with_equalities = []

    global_groups = global_group_list()

    index_value = 1
    group_count = 2
    element_count = 1
    tmp_globals = []
    tmp_pipes_in_globals = []
    for pipe in pipes_to_use_for_globals:
        if "global" in pipe and pipe not in tmp_globals:
            tmp_globals.append(pipe)
            pipes_in_global, global_config = get_global_pipe_config(pipe, sesam_jwt, base_url)
            if len(global_config['source']['equality']) != 0:
                list_of_global_pipes_with_equalities.append(global_config)
            global_pipes_config.append(global_config)
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
    total_length_of_list = len(global_groups)
    
    count = 1
    for group in global_groups:
        if "global" in group['name']:
            count = count +1
        if "global" not in group['name'] and "Default List" != group['name']:
            del global_groups[count+2:total_length_of_list]

    response_object = global_groups
    tmp_globals = []

    sesam_response = {"result": response_object, "pipe_configs_with_equalities": list_of_global_pipes_with_equalities}
    return {"pipes": pipes_to_use_for_globals}


## Create or update globals from existing SESAM integration
@app.route('/globals', methods=['POST'])
@cross_origin()
def get_globals():
    sesam_global_response = None
    global sesam_response
    global global_pipes_config
    connectors = request.json
    global_selection = connectors

    if global_selection['isEquality'] == True:
        global_names_used = []
        mapping_list_of_globals = []
        for pipe in global_pipes_config:
            mapping_list_of_globals.append(pipe['_id'])

        ## Updating an existing global
        if len(global_pipes_config) > 0:
            for element in global_selection['globalGroups']:
                for pipe_config in global_pipes_config:
                    if element['config']['_id'] == pipe_config['_id'] and element['config']['_id'] not in global_names_used:
                        global_names_used.append(element['config']['_id'])
                        pipe_config['source']['datasets'] = element['config']['source']['datasets']
                        pipe_config['source']['equality'] = element['config']['source']['equality']
                        update_global_with_equality(pipe_config, sesam_jwt, base_url)
                    else:
                        if element['config']['_id'] not in global_names_used and element['config']['_id'] not in mapping_list_of_globals:
                            global_name = element['config']['_id']
                            global_names_used.append(global_name)
                            create_global_with_equality(element['config'], sesam_jwt, base_url)

        ## Creating a new global   
        else:
            for element in global_selection['globalGroups']:
                global_name = element['config']['_id']
                if global_name not in global_names_used:
                    create_global_with_equality(element['config'], sesam_jwt, base_url)
    else:
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
        global_names_used = []
        datasets_used = []
        index = 1
        mapping_list_of_globals = []
        for pipe in global_pipes_config:
            mapping_list_of_globals.append(pipe['_id'])

        ## Updating an existing global
        if len(global_pipes_config) > 0:
            for element in selected_globals:
                for pipe_config in global_pipes_config:
                    if element['name'] == pipe_config['_id'] and element['name'] not in global_names_used:
                        global_names_used.append(element['name'])
                        for pipe, dataset in zip_longest(element['items'], pipe_config['source']['datasets']):
                            if pipe == None:
                                pass
                            if pipe == None and dataset != None:
                                pipe = {'name': 'Denmark'}
                            if dataset != None and pipe['name'] == dataset.split(' ')[0]:
                                datasets_used.append(pipe['name'])
                                pipe_names.append(dataset)
                                index = index + 1
                            else:
                                if pipe['name'] not in datasets_used and pipe['name'] != 'Denmark':
                                    pipe_names.append(f"{pipe['name']} pip{index}")
                                    index = index + 1
                        update_global(pipe_config, pipe_names, sesam_jwt, base_url)
                        pipe_names = []
                        index = 1

                    else:
                        if element['name'] not in global_names_used and element['name'] not in mapping_list_of_globals:
                            global_name = element['name']
                            global_names_used.append(global_name)
                            for pipe in element['items']:
                                pipe_names.append(f"{pipe['name']} pip{index}")
                                index = index + 1
                            create_global(global_name, pipe_names, sesam_jwt, base_url)
                            pipe_names = []
                            index = 1

        ## Creating a new global   
        else:
            for element in selected_globals:
                global_name = element['name']
                if global_name not in global_names_used:
                    for pipe in element['items']:
                        pipe_names.append(f"{pipe['name']} pip{index}")
                        index = index + 1
                    create_global(global_name, pipe_names, sesam_jwt, base_url)
                    pipe_names = []
                    index = 1
    
    global_pipes_config = []

    sesam_response = {
        "sesam_result": "Your global pipes have been created and/or updated! ;)"
    }
    return {"system_result": sesam_global_response}


## General response...
@app.route('/sesam_response', methods=['GET'])
def sesam_result():
    global sesam_response
    return sesam_response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)