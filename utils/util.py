import os
import json
import robocorp.log as logger
from robocorp import workitems



@staticmethod
def get_environment_variables():
    # Define the directory where the env.json file is located
    item = workitems.inputs.current
    print("Received payload:", item.payload)
    
    devdata_dir = "devdata"
    env_file = os.path.join(devdata_dir, "env.json")

    if os.path.exists(env_file):
        with open(env_file, "r") as file:
            env_data = json.load(file)

        # Access the variables from the JSON
        url_site = env_data.get("url_site")
        phrase_test = env_data.get("phrase_test")
        section = env_data.get("section")
        data_range = env_data.get("data_range")
        sort_by = env_data.get("sort_by")

        # Now you can use these variables as needed
        return {
            "url_site": url_site,
            "phrase_test": phrase_test,
            "section": section,
            "data_range": data_range,
            "sort_by": sort_by,
        }
    else:
        logger.info("The env.json file was not found in the devdata directory.")
        return None
    
    

from robocorp.tasks import task

@task
def handle_item():

    workitems.outputs.create(payload={"key": "value"})