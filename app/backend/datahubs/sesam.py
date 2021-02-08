import requests
import logging
import json

def get_all_input_pipes(sesam_jwt, sesam_base_url):
    pipe_names = []
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content-type": "application/json"
    }
    sesam_response = requests.get(f"{sesam_base_url}/pipes",
                                  headers=header,
                                  verify=False)

    if not sesam_response.ok:
        return "Could not fetch pipes from Sesam"

    else:
        for pipe in sesam_response.json():
            if "endpoint" in pipe['_id'] or "output" in pipe[
                    '_id'] or "outgoing" in pipe[
                        '_id'] or "preparation" in pipe[
                            '_id'] or "enrich" in pipe['_id']:
                pass
            else:
                pipe_names.append(pipe['_id'])

    return pipe_names

def create_global(global_name, selected_pipes, sesam_jwt, sesam_base_url):
    return_msg = None
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content-type": "application/json"
    }
    global_pipe = {
        "_id": f"{global_name}",
        "type": "pipe",
        "source": {
            "type": "merge",
            "datasets": selected_pipes,
            "identity": "first",
            "strategy": "default",
            "version": 2
        },
        "metadata": {
            "global": True,
            "tags": [f"{global_name.split('-')[1]}"]
        },
    }

    sesam_response = requests.post(f"{sesam_base_url}/pipes",
                                   headers=header,
                                   data=json.dumps([global_pipe]),
                                   verify=False)
    if not sesam_response.ok:
        response = json.loads(sesam_response.content.decode('utf-8-sig'))
        if response['detail'] == f"The pipe '{global_name}' already exists!":
            print(f'Trying to update config of {global_name}...')
            sesam_second_response = requests.put(f"{sesam_base_url}/pipes/{global_name}/config",
                                   headers=header,
                                   data=json.dumps(global_pipe),
                                   verify=False)
            if not sesam_second_response.ok:
                print(sesam_second_response.content)
            
            else:
                print(f"Pipe '{global_pipe['_id']}' has been updated")
                return_msg = "Global updated"
    
    else:
        print(f"Pipe '{global_pipe['_id']}' has been created")
        return_msg = "Global created"

    return return_msg

def get_all_pipes(sesam_jwt, sesam_base_url):
    pipe_names = []
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content-type": "application/json"
    }
    sesam_response = requests.get(f"{sesam_base_url}/pipes",
                                  headers=header,
                                  verify=False)

    if not sesam_response.ok:
        err_msg = ["Could not fetch pipes from Sesam.", "Make sure your provided URL and JWT are valid and try again by refreshing."]
        return err_msg

    else:
        for pipe in sesam_response.json():
            pipe_names.append(pipe['_id'])

    return pipe_names

def get_global_pipe_config(global_pipe, sesam_jwt, sesam_base_url):
    pipes_in_global = []
    header = {
        'Authorization': f'Bearer {sesam_jwt}',
        "content-type": "application/json"
    }
    sesam_response = requests.get(f"{sesam_base_url}/pipes/{global_pipe}/config",
                                  headers=header,
                                  verify=False)

    if not sesam_response.ok:
        err_msg = ["Could not fetch pipes from Sesam.", "Make sure your provided URL and JWT are valid and try again by refreshing."]
        return err_msg

    else:
        json_config = json.loads(sesam_response.content.decode('utf-8-sig'))
        datasets = json_config['source']['datasets']
        for element in datasets:
            pipes_in_global.append(element.split(' ')[0])

    return pipes_in_global