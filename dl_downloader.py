from tqdm import tqdm
import json
import os
import re
import requests
import dl_utils as utils
import dl_object_init as dl

import eyed3
import mutagen
from mutagen.easyid3 import EasyID3

def add_to_download_log(Downloader):
    pass

def applymetadata(download_object):
    try:
        new = EasyID3(download_object["path"])
    except mutagen.id3.ID3NoHeaderError:
        new = mutagen.File(download_object["path"], easy = True)
        new.add_tags()

    #print(EasyID3.valid_keys.keys())

    new["albumartist"] = download_object["metadata"]["artist"]
    new["artist"] = download_object["metadata"]["artist"]
    new["album"] = download_object["metadata"]["playlist"]
    new["tracknumber"] = str(download_object["metadata"]["track number"])
    new["title"] = download_object["metadata"]["title"]
    new["date"] = str(download_object["metadata"]["year"])

    new.save()

def download(Downloader):
    if Downloader.objects_list[Downloader.current].site == "youtube" or Downloader.objects_list[Downloader.current].site == "bandcamp":
        folder_path = Downloader.objects_list[Downloader.current].download_info[0]
        if os.path.exists(folder_path) != True:
            os.mkdir(folder_path)

    for download_object in Downloader.objects_list[Downloader.current].download_info:

        if isinstance(download_object, dict):
            output_path = download_object["path"]
            url = download_object["contents"]

            if download_object["text file"] == True:
                utils.file_write(output_path,url)

            if Downloader.settings["debug"]["print download info"] == True:
                print(utils.print_json(download_object))

            if Downloader.settings["debug"]["download"] == True and download_object["download"] == True:
                print("Downloading to: {}".format(output_path)) #CHange this print statement
                r = requests.get(url, stream=True)

                total_size = int(r.headers.get('content-length', 0))

                size = utils.byte_converter(total_size)

                block_size = 1024 #1 Kibibyte

                t=tqdm(total=total_size, unit='iB', unit_scale=True)  #Solved by running in python(w).exe via task scheduler

                with open(output_path, 'wb') as f:
                    for data in r.iter_content(block_size):
                        t.update(len(data))
                        f.write(data)
                t.close()

                #Also needs thumbnails lol

                if re.search(r'.mp3',output_path) != None: #Should be filename not path.
                    applymetadata(download_object)
                
    return Downloader

if __name__ == "__main__":
    def Tester():
        applymetadata(
            {
            "path":r"C:\Utilities\Scripts\url-dl-v2 output\test_file.mp3",
            "text file": False,
            "download": True,
            "contents": True,
            "thumbnail": None,
            "merge audio": None,
            "metadata": { #Need to apply later.
                "title":"lol",
                "artist":"artist",
                "track number":"track num",
                "playlist":"playlist",
                "year":"2010"
                }
            }
        )

    #Tester()

    