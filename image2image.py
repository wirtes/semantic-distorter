#!/usr/bin/python

import requests
import json
import semantic_distorter

# Setup Global Variables
config = semantic_distorter.get_config("/home/pi/botcode")
api_key = config["wizmodel_api_key"]

url = "https://api.wizmodel.com/sdapi/v1/img2img"

payload = json.dumps(
    {
        "prompt": "thick oil paint, canvas texture",
        "init_images": [
            "https://www.wirtes.com/images/The-Family.jpg"
        ],
    }
)
headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
 
response = requests.request("POST", url, headers=headers, data=payload)

semantic_distorter.save_image_from_json(response, config["working_directory"] + '/images/autogen/image_2_image.png')