import re
import json
import requests
import time
from resources.dl_items import i

def file_write(path,text):
    text = str(text)
    with open(path,'w', encoding = 'utf-8') as f:
        f.write(text)

def apostrophe(text): #For  all string issues
    return (text.replace("*","")
                .replace(":","")
                .replace("\\","_")
                .replace("//","_")
                .replace("?","")
                .replace("amp;","")
    )

def print_json(data):
    print(json.dumps(data, indent=4, sort_keys=True))

def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True)

def source_code(link): #may change
    response = requests.get(link) 
    if response.status_code == 200:
        pass
    else:
        local.log(response.status_code)
    text = response.content
    #esp the unicode part - maybe change completely, edit it afterwards - may compare to bs4's implementations
    text = text.decode()
    text = str(text.encode(encoding='utf-8'))
    return text

def string_escape(s):
    return (s.encode('latin1',"ignore")         # To bytes, required by 'unicode-escape'
                .decode('unicode-escape') # Perform the actual octal-escaping decode
                .encode('latin1',"ignore")         # 1:1 mapping back to bytes
                .decode("utf-8",'ignore'))

def give_it_some_time():
    time.sleep(0.1)

def byte_converter(size):
    ext = None
    if size/1000 > 1:
        size = size/1000
        size = int(size)
        ext = "KB"
        if size/1000 > 1:
            size = size/1000
            ext = "MB"
            if size/1000 > 1:
                size = size/1000
                size = "{0:.2f}".format(size)
                ext = "GB"
            else:
                size = "{0:.2f}".format(size)
    return str(size) +" "+ ext

#regexes
year_regex = re.compile(r'20[0-9][0-9]|19[0-9][0-9]')
img_regex = re.compile(r'(?<=.)jpg|(?<=.)gif|(?<=.)png|(?<=.)psd|(?<=.)tif')
audio_regex = re.compile(r'(?<=.)mp3|(?<=.)m4a|(?<=.)flac|(?<=.)ogg|(?<=.)wav')