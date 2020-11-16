#temp -- move pls
main_dir = r"C:\Users\chang\Documents\Utilities\url-dl-v2"

import time
import os
import sys
import json
import re
from resources.dl_items import *
import dl_utils as utils
import dl_downloader as download
import dl_object_init as dl

os.chdir(main_dir)

def main(tgt):
    global Downloader
    Downloader = dl.RunInfo()
    Downloader.target_status = tgt
    load_settings()
    create_output_directory()
    parse_input(Downloader)

def load_settings():
    with open("settings.json") as f:
        Downloader.settings = json.load(f)

def parse_input(Downloader):
    download_list = []
    if Downloader.target_status == "local":
        path = "Links.txt"
        with open(path,"r") as f:
            for line in f.readlines():
                if line.startswith("##") == False:
                    download_list.append(re.search(r'.*(?=\n)',line).group())

    elif Downloader.target_status == "network":
        path = None
        raise Exception("WIP")
        breakpoint()
    
    for count, dl_object_string in enumerate(download_list):
        if count < Downloader.settings["max download"]:
            a = dl.DownloadObject()
            Downloader.objects_list.append(a)
            Downloader.current = count
            dl_object_string += " "

            dl_object = Downloader.objects_list[count]

            if dl_object_string.startswith("http") == True:
                dl_object.object_type = "url"
            else:
                dl_object.object_type = "non_url"

            ##log
            print("Current: {}".format(dl_object_string))

            #youtube
            link_match = re.search(r'(https).*(youtu).*(?= )',dl_object_string)
            if link_match != None:
                dl_object.data["url"] = link_match.group()
                from extractors.youtube import youtube_extractor
                Downloader = youtube_extractor(Downloader)

            #Download handler
            Downloader = download.download(Downloader)
            #convert NOTNWNTOWNOONONOWWWWW

def create_output_directory():
    directories = Downloader.settings["directories"]
    root = directories["output"]
    if os.path.exists(root):
        pass
    else:
        os.mkdir(root)

    for f in list(directories["output folders"]):
        folder = directories["output folders"][f]
        path = os.path.join(root,f)
        if os.path.exists(path):
            pass
        else:
            os.mkdir(path)
            if isinstance(folder,dict) and len(folder) > 0:
                for folder_2 in folder:
                    path = os.path.join(path,folder_2)
                    if os.path.exists(path):
                        pass
                    else:
                        os.mkdir(path)

def create_settings(): #template for file
    settings = {}
    settings["debug"] = {}
    settings["debug"]["download"] = True
    settings["debug"]["foo"] = "bar"

    file_write("settings.json",json.dumps(settings, indent=4, sort_keys=True))

main("local")