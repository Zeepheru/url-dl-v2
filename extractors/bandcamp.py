import sys
import re

def tester(): #for all extractors
    from os import getcwd #may have to open the folder in VSC to get correct working directory (otherwise is [:-11])
    sys.path.append(getcwd()) #needed for testing only

if __name__ == "__main__":
    tester()

from bs4 import BeautifulSoup
import requests
import json
import os
import dl_utils as utils
import settings
import dl_object_init as dl

import dl_logger as dl_logger

test_links = [
    "https://vyletpony.bandcamp.com/album/super-pony-world-fairytails"
]

def extractor_test_setup():
    def create_objects():
        some_list = []
        for count, a in enumerate(test_links):
            some_list.append(dl.DownloadObject()) #test
            some_list[count].data["url"] = a
        return some_list

    Downloader = dl.RunInfo()
    Downloader.settings = settings.load_settings()
    Downloader.objects_list = create_objects()

    return Downloader

##END OF TEMPLATE CODE

def bandcamp_extractor(Downloader):
    global dl_object
    dl_object = Downloader.objects_list[Downloader.current]
    dl_object.site = "bandcamp"
    data = dl_object.data
    data["sub_objects"] = []

    try:
        data["url"].replace(' ','')
    except:
        pass

    #BS4 for playlist art
    response = requests.get(data["url"])
    response.raise_for_status()
    soup = BeautifulSoup(response.text,'lxml')
    data["thumbnail url"] = soup.find(attrs={"id":"tralbumArt"}).contents[1]["href"]

    text = utils.source_code(data["url"]).replace("&quot;",'"')
    #utils.file_write('Test_1.txt',text)
                
    texta = re.search(r'(?<=data-tralbum=").*?}(?=")',text,re.DOTALL).group()
    #utils.file_write('Test_2.txt',texta)

    json_data = json.loads(utils.string_escape(texta))
    #utils.file_write('Test_3.txt',utils.dump_json(json_data))

    data["playlist"] = json_data["current"]["title"].replace("amp;","")
    data["artist"] = json_data["artist"]
    data["year"] = re.search(utils.year_regex,json_data["current"]["publish_date"]).group()

    if int(json_data["current"]["minimum_price"]) == 0:
        dl_logger.log_info("This album can be downloaded for free.")

    for track in json_data["trackinfo"]:
        track_info = {}
        track_info["title"] = track["title"].replace("amp;","")
        track_info["url"] = track["file"]["mp3-128"] #possible more formats in other links?
        track_info["track number"] = track["track_num"]

        data["sub_objects"].append(track_info)

    download_handler(Downloader)
    return Downloader
    
def download_handler(Downloader):
    dl_object = Downloader.objects_list[Downloader.current]
    root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"bandcamp",utils.apostrophe(dl_object.data["playlist"]))
    dl_object.download_info.append(root_download_dir)

    for track_info in dl_object.data["sub_objects"]:

        #streams = sub_object["streams"]

        #Main File
        if track_info["url"].startswith("http") == True:
            filename = utils.apostrophe(track_info["title"])+"."+"mp3"
            dl_object.download_info.append({
                "filename":filename,
                "path":(os.path.join(root_download_dir,filename)),
                "text file": False,
                "download": True,
                "contents": track_info["url"],
                "thumbnail": dl_object.data["thumbnail url"],
                "merge audio": None,
                "metadata": { #Need to apply later.
                    "title":track_info["title"],
                    "artist":dl_object.data["artist"],
                    "track number":track_info["track number"],
                    "playlist":dl_object.data["playlist"],
                    "year":dl_object.data["year"]
                }
            })
        else:
            dl_logger.log_info("Audio stream undownloadable") #log some form of error
        #Seperate cover art
    dl_object.download_info.append({
        "filename":"Cover Art"+"."+re.search(utils.img_regex,dl_object.data["thumbnail url"]).group(),
        "path":(os.path.join(root_download_dir,"Cover Art"+"."+re.search(utils.img_regex,dl_object.data["thumbnail url"]).group())),
        "text file": False,
        "download": True,
        "contents": dl_object.data["thumbnail url"],
        "thumbnail": None,
        "merge audio": None
    })
    #utils.print_json(dl_object.download_info)
        

if __name__ == "__main__":
    
    Downloader = extractor_test_setup()
    dl_logger.init_logger(Downloader.settings["directories"]["main"], "bandcamp")
    for i in range(len(test_links)):
        Downloader.current = i
        bandcamp_extractor(Downloader)