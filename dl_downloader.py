from tqdm import tqdm
import json
import os
import re
import requests
import dl_utils as utils
import dl_object_init as dl

def download(Downloader):
    if Downloader.objects_list[Downloader.current].site == "youtube":
        folder_path = Downloader.objects_list[Downloader.current].download_info[0]
        if os.path.exists(folder_path) != True:
            os.mkdir(folder_path)
    for download_object in Downloader.objects_list[Downloader.current].download_info:
        if isinstance(download_object, dict):
            output_path = download_object["path"]
            url = download_object["contents"]

            if download_object["text file"] == True:
                utils.file_write(output_path,url)

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
                
    return Downloader