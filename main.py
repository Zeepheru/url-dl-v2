#temp -- move pls
main_dir = r"C:\Users\chang\Documents\Utilities\url-dl-v2"

import time
import os
import sys
import json
import re
from resources.dl_items import *
from dl_utils import *

os.chdir(main_dir)

class RunInfo(): #todo import this class in all files
    def __init__(self):
        self.target_status = None
        self.settings = {}
        self.start_time = time.time()
        self.objects_list = []
        self.current = 0

    def get_duration(self): #duration in seconds
        breakpoint()
        return time.time() - self.start_time

        def beautify(): #Deal with this later
            duration_s = time.time()-start_time_int
            if duration_s >= 60:
                duration_m = int(duration_s/60)
                duration_s = duration_s % 60
                
                if duration_m >= 60:
                    duration_h = int(duration_m/60)
                    duration_m = duration_m % 60
                else:
                    duration_h = 0
            else:
                duration_m,duration_h = 0,0
            duration_s = "{:.2f}".format(duration_s)

    def lol():
        pass

class DownloadObject():
    def __init__(self):
        self.object_type = None
        self.site = None
        self.data = {}

def main(tgt):
    global downloader
    downloader = RunInfo()
    downloader.target_status = tgt
    load_settings()
    create_output_directory()
    parse_input()

def load_settings():
    with open("settings.json") as f:
        downloader.settings = json.load(f)

def parse_input():
    download_list = []
    if downloader.target_status == "local":
        path = "Links.txt"
        with open(path,"r") as f:
            for line in f.readlines():
                if line.startswith("##") == False:
                    download_list.append(re.search(r'.*(?=\n)',line).group())

    elif downloader.target_status == "network":
        path = None
        raise Exception("WIP")
        breakpoint()

    for count, dl_object_string in enumerate(download_list):
        a = DownloadObject()
        downloader.objects_list.append(a)
        downloader.current = count
        dl_object_string += " "

        dl_object = downloader.objects_list[count]

        if dl_object_string.startswith("http") == True:
            dl_object.object_type = "url"
        else:
            dl_object.object_type = "non_url"

        #youtube
        link_match = re.search(r'(https).*(youtu).*(?= )',dl_object_string)
        if link_match != None:
            dl_object.data["url"] = link_match.group()
            from extractors.youtube import youtube_extractor

def create_output_directory():
    directories = downloader.settings["directories"]
    root = directories["output"]
    if os.path.exists(root):
        pass
    else:
        os.mkdir(root)

    for f in list(directories["output folders"]):
        folder = directories["output folders"][f]
        path = os.path.join(root,folder)
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