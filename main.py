import json


## get config data
config_filename = "config.json"

def get_config(filename):

    try:
       with open(filename) as f:
           data = json.load(f)
           return data
    except Exception as e:
        print("Error: ", e)

config_data = get_config(config_filename)

print(config_data)