import re
import json
import requests
import time
from resources.dl_items import i
import urllib
from selenium import webdriver

def file_write(path,text):
    text = str(text)
    with open(path,'w', encoding = 'utf-8') as f:
        f.write(text)

def apostrophe(text): #For  all string issues
    return (text.replace("*","")
                .replace(":","")
                .replace("\\","_")
                .replace("//","_")
                .replace("\m"[0:1],"_")
                .replace("/","_")
                .replace("?","")
                .replace("amp;","")
                .replace('"',"'")
                .replace('|'," ")
    )

def give_me_the_time():
    return time.strftime("%Y %m %d %H.%M.%S")

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

def source_code_b(link): #may change
    with urllib.request.urlopen(link) as response:
        return response.read().decode('utf-8')

def source_code_c(link):
    url = link
    driver = webdriver.Firefox()
    driver.get(url)
    SCROLL_PAUSE_TIME = 0.25

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    return driver.page_source


def string_escape(s):
    return (s.encode('latin1',"ignore")         # To bytes, required by 'unicode-escape'
                .decode('unicode-escape') # Perform the actual octal-escaping decode
                .encode('latin1',"ignore")         # 1:1 mapping back to bytes
                .decode("utf-8",'ignore'))

def give_it_some_time():
    time.sleep(0.1)

def byte_converter(size):
    ext = "B"
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

def re_double_backslash(string):
    return string.replace("\\"[0:1],"\\")

#regexes
year_regex = re.compile(r'20[0-9][0-9]|19[0-9][0-9]')
img_regex = re.compile(r'(?<=.)jpg|(?<=.)gif|(?<=.)png|(?<=.)psd|(?<=.)tif')
audio_regex = re.compile(r'(?<=.)mp3|(?<=.)m4a|(?<=.)flac|(?<=.)ogg|(?<=.)wav')

parent_dir_regex = re.compile(r'.*(?=\\)')