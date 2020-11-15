import time
import os
import sys
import json
import re
from resources.dl_items import *
import dl_utils as utils
import settings
import dl_object_init as dl

main_dir = os.getcwd()
os.chdir(main_dir)


def main(tgt):
    global Downloader
    Downloader = dl.RunInfo()
    Downloader.target_status = tgt
    Downloader.start_time = time.time()
    Downloader.settings = settings.load_settings()

    create_output_directory()
    parse_input()

def parse_input():
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
        a = dl.DownloadObject()
        Downloader.objects_list.append(a)
        Downloader.current = count
        dl_object_string += " "

        dl_object = Downloader.objects_list[count]

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
    directories = Downloader.settings["directories"]
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



settings.lol()
#main("local")