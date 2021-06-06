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
    "https://monster-siren.hypergryph.com/music/"
]

"""
2021-06-05

https://monster-siren.hypergryph.com/music/
This site. Seems to be some Chinese stuff (as evidenced by the BiliBili link to the channel there)

json containing all the required links, from the HTML of the above link (musicpage.html) is available 
as .\extractors\custom\musicpage.json

! may rename the folders or files in the future, do take note.
"""

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

def custom_extractor_a(Downloader):
    global dl_object
    dl_object = Downloader.objects_list[Downloader.current]
    dl_object.site = "monster_siren_hypergryph" #lol
    data = dl_object.data
    data["sub_objects"] = []
    ## each sub_object is an album

    try:
        data["url"].replace(' ','')
    except:
        pass

    if data["url"][-1:] != "/":
        ## in case, need for later, need to make sure the end of the url is [.../music/]
        data["url"] += "/"

    with open(os.path.join(Downloader.settings["directories"]["main"], r"extractors\custom\musicpage.json"),
             "r", encoding="utf-8") as f:
        ## loading json from the file already present.    
        music_info = json.load(f) # or loads, idk.

    albums = [None] * 10000 
    ## list of albums, with the albums appended based on their cid
    ## tracks are added to this later based on their album

    tracks = []
    ## no need for indexing

    ## Variables with [_info] are scraped from the html/json

    for album_info in music_info["music"]["albumList"]:
        
        album_info["tracks"] = []
        ## for later

        ### code for changing the artistes list to a string 
        artist_string = ""
        for i, a in enumerate(album_info["artistes"]):
            if i == 0:
                artist_string += a
            elif i < len(album_info["artistes"]) and len(album_info["artistes"]) > 2:
                artist_string += ", " + a
            else:
                artist_string += ", " + a

        album_info["artistes"] = artist_string
        del artist_string
        ###

        albums[int(album_info["cid"])] = album_info
        ## writes the album to the list based on its cid.

    dl_logger.log_info("Finished sifting albums.")

    """
    Example album
    {
        "cid":"0253",
        "name":"Tipsy",
        "coverUrl":"https:\u002F\u002Fweb.hycdn.cn\u002Fsiren\u002Fpic\u002F20210322\u002Fb62ff3caf8c32adbba41325644ccab49.jpg",
        "artistes":[
        "塞壬唱片-MSR"
        ]
    },
    """ #tracks are added later
    
    for i, track_info in enumerate(music_info["player"]["list"]):
        if i == 10000: # for testing, to reduce numver of tracks. 
            # (lazy to remove from code, have a large int instead)
            break

        dl_logger.log_info("Currently scraping: {}".format(track_info["cid"]))
        
        ### code for extracting the file url from the html.
        r = requests.get(data["url"] + track_info["cid"])
        r.raise_for_status()
        
        #
        track_info_json = re.search(r'(?<=window.g_initialProps = ).*(?=}};)',r.text ,flags=re.DOTALL).group()
        track_info_json += r"}}"
        track_info_json = track_info_json.replace("undefined",'""') # lol
        track_info_json = json.loads(track_info_json)
        # classic it wil go wrong here XD

        track_info["url"] = track_info_json["player"]["songDetail"]["sourceUrl"]
        # hope this works

        """ example snippet (un-indented), may have to replace unicode stuff
        d":"880375","name":"Synthetech","albumCid":"4527","artists":["塞壬唱片-MSR"]}],"mode":"list",
        "current":"514587","volume":50,"isPlaying":false,"isMute":false,"songDetail":{"cid":"514587",
        "name":"Real Me","albumCid":"0250","sourceUrl":"https:\u002F\u002Fres01.hycdn.cn\u002F7c2a47d
        975977498bd76e79a4a1710ea\u002F60BB472C\u002Fsiren\u002Faudio\u002F20210531\u002F548540c229d9
        015df8c1e03884dfb197.mp3","lyricUrl":null,"mvUrl":null,"mvCoverUrl":null,"artists":["塞壬唱片-MSR"]},
        "initial":true},"section":{"layoutStatus":{"layoutStatus":{},"canRoute":false,"pageStatus":{},
        "Layout":{"
        """

        del r
        ###

        ### code for changing the artistes list to a string 
        artist_string = ""
        for i, a in enumerate(track_info["artists"]):
            if i == 0:
                artist_string += a
            elif i < len(track_info["artists"]) and len(track_info["artists"]) > 2:
                artist_string += ", " + a
            else:
                artist_string += ", " + a

        track_info["artists"] = artist_string
        del artist_string
        ###
 
        track_info["track number"] = len(albums[int(track_info["albumCid"])]["tracks"]) + 1
        ### code to add the track number based on the current length of "tracks". 
        ### I know this is incorrect, but I'm lazy to get the actual track number from the tracks' html

        albums[int(track_info["albumCid"])]["tracks"].append(track_info)
        ## adds the tracks to the albums.

    """
    example track
    {
        "cid":"514587",
        "name":"Real Me",
        "albumCid":"0250",
        "artists":[
        "塞壬唱片-MSR"
        ],
        "url":"",
        "track number":n
    },
    """
    data["sub_objects"] = [album for album in albums if album != None] # list comprehension

    download_handler(Downloader)
    return Downloader
    
def download_handler(Downloader):
    dl_logger.log_info("Writing download info to Downloader.")

    dl_object = Downloader.objects_list[Downloader.current]
    # no longer need to append a dir string into dl_objects (deprecated by createallfolders)

    """
    Example full album dict
    {
        "cid":"0253",
        "name":"Tipsy",
        "coverUrl":"https:\u002F\u002Fweb.hycdn.cn\u002Fsiren\u002Fpic\u002F20210322\u002Fb62ff3caf8c32adbba41325644ccab49.jpg",
        "artistes":"塞壬唱片-MSR, blah",
        "tracks":[
            {
                "cid":"514587",
                "name":"Real Me",
                "albumCid":"0250",
                "artists":"塞壬唱片-MSR, blah",
                "url":"",
                "track number":n
            },
        ]
    },
    """

    for album in dl_object.data["sub_objects"]:
        if album["tracks"] == []:
            ## empty album, do not add to downloader.
            continue

        root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"other",
        utils.apostrophe(album["name"]))

        for track in album["tracks"]:
            ### audio tracks
            if track["url"].startswith("http") == True:
                fileformat = re.search(utils.audio_regex, track["url"][-6:]).group()
                ## Extracts the file format 

                filename = utils.apostrophe(track["name"]) + "." + fileformat
                dl_object.download_info.append({
                    "filename":filename,
                    "path":(os.path.join(root_download_dir,filename)),
                    "text file": False,
                    "download": True,
                    "contents": track["url"],
                    "thumbnail": album["coverUrl"],
                    "merge audio": None,
                    "metadata": { #Need to apply later.
                        "title":track["name"],
                        "artist":track["artists"],
                        "track number":track["track number"],
                        "playlist":album["name"],
                    }
                })

                del fileformat
            else:
                dl_logger.log_info("Audio stream undownloadable") #log some form of error

        ### Cover art
        fileformat = re.search(utils.img_regex, album["coverUrl"]).group()

        dl_object.download_info.append({
            "filename":"Cover Art" + "." + fileformat,
            "path":(os.path.join(root_download_dir,"Cover Art" + "." + fileformat)),
            "text file": False,
            "download": True,
            "contents": album["coverUrl"],
            "thumbnail": None,
            "merge audio": None
        })

        del fileformat

    #utils.print_json(dl_object.download_info)

    """
    Current test output
    No issues, only the logger cannot log at times (harmless errors.)
    [
        {
            "contents": "https://res01.hycdn.cn/3607dc9a19e9c562ae3c777adab79002/60BBD978/siren/audio/20210531/548540c229d9015df8c1e03884dfb197.mp3",
            "download": true,
            "filename": "Real Me.mp3",
            "merge audio": null,
            "metadata": {
                "artist": "\u585e\u58ec\u5531\u7247-MSR",
                "playlist": "Real Me",
                "title": "Real Me",
                "track number": 1
            },
            "path": "C:\\Utilities\\Scripts\\url-dl-v2 output\\other\\Real Me\\Real Me.mp3",
            "text file": false,
            "thumbnail": "https://web.hycdn.cn/siren/pic/20210531/64eb57d1af5fbff9897633d06e1c3981.jpg"
        },
        {
            "contents": "https://web.hycdn.cn/siren/pic/20210531/64eb57d1af5fbff9897633d06e1c3981.jpg",
            "download": true,
            "filename": "Cover Art.jpg",
            "merge audio": null,
            "path": "C:\\Utilities\\Scripts\\url-dl-v2 output\\other\\Real Me\\Cover Art.jpg",
            "text file": false,
            "thumbnail": null
        },
        {
            "contents": "https://res01.hycdn.cn/966cd82cf30ca8d0a7e97d3fcbdf1854/60BBD97A/siren/audio/20210501/786e9cb8649a1aed0d6f97bde26729b3.mp3",
            "download": true,
            "filename": "Immutable (Instrumental).mp3",
            "merge audio": null,
            "metadata": {
                "artist": "\u585e\u58ec\u5531\u7247-MSR",
                "playlist": "Immutable",
                "title": "Immutable (Instrumental)",
                "track number": 1
            },
            "path": "C:\\Utilities\\Scripts\\url-dl-v2 output\\other\\Immutable\\Immutable (Instrumental).mp3",
            "text file": false,
            "thumbnail": "https://web.hycdn.cn/siren/pic/20210501/01bdad2a0a6876eaee3c23bf0812a73a.png"
        },
        {
            "contents": "https://web.hycdn.cn/siren/pic/20210501/01bdad2a0a6876eaee3c23bf0812a73a.png",
            "download": true,
            "filename": "Cover Art.png",
            "merge audio": null,
            "path": "C:\\Utilities\\Scripts\\url-dl-v2 output\\other\\Immutable\\Cover Art.png",
            "text file": false,
            "thumbnail": null
        }
    ]
    """
        

if __name__ == "__main__":
    
    Downloader = extractor_test_setup()
    dl_logger.init_logger(Downloader.settings["directories"]["main"], "other")
    for i in range(len(test_links)):
        Downloader.current = i
        custom_extractor_a(Downloader)