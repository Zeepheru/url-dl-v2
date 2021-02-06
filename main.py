#temp -- move pls
import time
import os
import sys
import json
import re
from resources.dl_items import *
import dl_utils as utils
import dl_downloader as download
import dl_object_init as dl

import dl_logger as dl_logger

def main(tgt):
    Downloader.target_status = tgt
    #print(Downloader.settings["debug"]["print download info"])
    create_output_directory()
    parse_file(Downloader)

def load_settings():
    with open("settings.json") as f:
        Downloader.settings = json.load(f)

def parse_input():
    global Downloader
    print(
"""Downloader Utility.
--help for list of all commmands""")

    help_msg = """
Command list:

--help - What you are doing now.

settings - At the moment only prints the settings, need to change in settings.json manually.
run - Loads links from default link file.
close - closes utility. (alternate options are alt-f4, closing the window)
load_json - loads download info from a parsed download.json, in the default jsons directory.

dl - downloads single link behind, or:
dl -derpi - special Derpibooru downloader, (WIP)
dl -youtube - idk what the hell to do here for now.
"""
    while 1 > 0:
        #print("yes this is happening again" + str(Downloader.auto_command))
        if (Downloader.settings["debug"]["autocommand"] != None or Downloader.settings["debug"]["autocommand"] != "") and Downloader.auto_command == False:
            user_input = Downloader.settings['debug']["autocommand"]
            dl_logger.log_info("Autocommand from settings: {}".format(user_input))       
            Downloader.auto_command = True                                                
        else:
            user_input = input()

        dl_logger.log_to_file("Command: {}".format(user_input))


        try:
            command_1 = re.search(r'.*?(?= )',user_input).group()
        except:
            command_1 = user_input
        try:
            command_2 = re.search(r'(?<= ).*',user_input).group()
        except:
            command_2 = ""
            
        if command_1 == "--help":
            print(help_msg)
        elif command_1 == "run": 
            main("local")
        elif command_1 == "settings":
            utils.print_json(Downloader.settings)
        elif command_1 == "close":
            break
        elif command_1 == "load_json":
            json_to_load = os.path.join(Downloader.settings["directories"]["json"],command_2)
            with open(json_to_load,encoding = "utf-8") as f:
                json_to_load = f.read()
            current = json.loads(json_to_load)
            if Downloader.current != 0:
                Downloader.current += 1
            a = dl.DownloadObject()
            a.download_info = current
            a.site = re.search(r'.*?(?=_)',command_2).group()
            Downloader.objects_list.append(a)
            
            download.download(Downloader)
            print("Download from json: {} complete.".format(command_2))

        elif command_1 == "dl":
            dl_cmd_error = False
            
            Downloader.target_status = "local"
            

            if command_2.startswith("-youtube") == True:
                command_link = re.search(r'(?<=-youtube ).*',command_2).group()
                if not command_link.startswith("http"):
                    dl_logger.log_info("{} Is not a link.".format(command_link))
                    dl_cmd_error = True
                else:
                    ##main yt_code (from below)
                    download_list = re.findall(r'.*?(?= )',command_link+" ")
                    for a_2 in download_list:
                        a_2 = a_2.replace(" ","")
                        if a_2 == "":
                            download_list.remove(a_2)
                        
                        elif not a_2.startswith("http"):
                            dl_logger.log_info("{} Is not a link.".format(a_2))
                            download_list.remove(a_2)

                    for count, dl_object_string in enumerate(download_list):
                        ##Overrides max dls for now
                        a = dl.DownloadObject()
                        Downloader.objects_list.append(a)
                        Downloader.current = count

                        dl_logger.log_to_file("youtube link")
                        Downloader.objects_list[count].data["url"] = dl_object_string
                        from extractors.youtube import youtube_extractor
                        print("Youtube Link. Extractor code may need to be edited if parsing takes too long, may mean a wrong regex because of changed html.")
                        Downloader = youtube_extractor(Downloader) #Downloader_2 because Downloader causes errors.

                        Downloader = download.download(Downloader)
                        dl_logger.log_info("Download for |{}| complete.\n".format(dl_object_string))
                        print("\n")

            else:
                dl_cmd_error = True
        #Appending links with a manual link add?

def parse_file(Downloader): #if run - is initialized
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

    if download_list == []:
        dl_logger.log_info("Download file is empty. (No links specified for download)")
    
    for count, dl_object_string in enumerate(download_list):
        try:
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
                dl_logger.log_info("Current: {}".format(dl_object_string))

                #NEED TO MOVE THIS OUT - seperate

                #youtube
                link_match = re.search(r'(http).*(youtu).*(?= )',dl_object_string)
                if link_match != None:
                    dl_logger.log_to_file("youtube link")
                    dl_object.data["url"] = link_match.group()
                    from extractors.youtube import youtube_extractor
                    print("Youtube Link. Extractor code may need to be edited if parsing takes too long, may mean a wrong regex because of changed html.")
                    Downloader = youtube_extractor(Downloader)

                #bandcamp
                link_match = re.search(r'(http).*(.bandcamp.com).*(?= )',dl_object_string)
                if link_match != None:
                    dl_logger.log_to_file("bandcamp link")
                    dl_object.data["url"] = link_match.group()
                    from extractors.bandcamp import bandcamp_extractor
                    Downloader = bandcamp_extractor(Downloader)

                #mediafire
                link_match = re.search(r'(http).*(.mediafire.com).*(?= )',dl_object_string)
                if link_match != None:
                    dl_logger.log_to_file("mediafire link")
                    dl_object.data["url"] = link_match.group()
                    from extractors.mediafire import mediafire_extractor
                    Downloader = mediafire_extractor(Downloader)

                #Download handler
                Downloader = download.download(Downloader)
                dl_logger.log_info("Download for {} complete.\n".format(dl_object_string.replace(" ","")))
                print("\n")

        except (IOError,NameError,Exception) as e:
            dl_logger.log_exception(e)

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
        if isinstance(folder,list) and len(folder) > 0:
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

if __name__ == "__main__":
    global Downloader
    Downloader = dl.RunInfo()
    load_settings()
    dl_logger.init_logger(Downloader.settings["directories"]["main"])
    try:
        parse_input()
            
    except (IOError,NameError,Exception) as e:
        dl_logger.log_exception(e)

    dl_logger.end_logger()
    #try:
    #except Exception as e:
        #print(e)    
        #input("Press Enter to continue")