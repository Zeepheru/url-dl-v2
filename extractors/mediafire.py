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

test_links = [
    r"http://www.mediafire.com/file/o2dxwhee16ia4xd/The_History_of_Ponyville-%2528by_MelodicPony%2529.flac/file" 
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

def mediafire_extractor(Downloader):
    global dl_object
    dl_object = Downloader.objects_list[Downloader.current]
    dl_object.site = "youtube"
    data = dl_object.data
    data["sub_objects"] = []
    dl_object.data["sub_objects"].append({})
    sub_object = dl_object.data["sub_objects"][0]

    response = requests.get(data["url"])
    response.raise_for_status()
    soup = BeautifulSoup(response.text,'lxml')
    sub_object["url"] = soup.find(attrs={"id":"downloadButton"})["href"]
    sub_object["filename"] = utils.apostrophe(utils.string_escape(re.findall(r'(?<=/).*?(?=/)',sub_object["url"]+"/")[-1]))
    download_handler(Downloader)

    return Downloader
    
def download_handler(Downloader):
    dl_object = Downloader.objects_list[Downloader.current]
    sub_object = dl_object.data["sub_objects"][0]
    filename = sub_object["filename"]

    root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"mediafire",)

    dl_object.download_info.append({
        "filename":filename,
        "path":(os.path.join(root_download_dir,sub_object["filename"])),
        "text file": False,
        "download": True,
        "contents": sub_object["url"],
        "thumbnail": None,
        "merge audio": None
    })
        
if __name__ == "__main__":
    
    Downloader = extractor_test_setup()
    for i in range(len(test_links)):
        Downloader.current = i
        mediafire_extractor(Downloader)