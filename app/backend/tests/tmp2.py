for element in selected_globals:
                    global_name = element['name']
                    if global_name == pipe_config['_id']:
                        global_to_skip = global_name
                        for pipe in element['items']:
                            pipe_names.append(f"{pipe['name']} pip{index}")
                            index = index + 1
                        update_global(pipe_config, pipe_names, sesam_jwt, base_url)
                        pipe_names = []
                        index = 1
            
                    else:
                        pass
                
            else:
                for element in selected_globals:
                    global_name = element['name']
                    print(f"For testing: {global_name}")
                    for pipe in element['items']:
                        pipe_names.append(f"{pipe['name']} pip{index}")
                        index = index + 1
                    create_global(global_name, pipe_names, sesam_jwt, base_url)
                    pipe_names = []
                    index = 1