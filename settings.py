import json
import os
import re
import dl_utils as utils
import dl_object_init as dl

def create_settings(): #template for file
    settings = {}
    settings["debug"] = {}
    settings["debug"]["download"] = True
    settings["debug"]["foo"] = "bar"

    utils.file_write("settings.json",json.dumps(settings, indent=4, sort_keys=True))

def change_settings_dir():
    new_root_dir = os.getcwd()
    parent_dir = re.search(r'.*(?=\\)',new_root_dir).group()
    ouptut_dir = os.path.join(parent_dir,"url-dl-v2 output")
    local_settings["directories"]["main"] = new_root_dir
    local_settings["directories"]["output"] = ouptut_dir
    save_settings(local_settings)

def save_settings(settings):
    utils.file_write("settings.json",json.dumps(settings, indent=4, sort_keys=True))

def load_settings():
    with open("settings.json") as f:
        settings = json.load(f)

    return settings

if __name__ == "__main__":
    #for changing settings
    local_settings = load_settings()
    change_settings_dir()