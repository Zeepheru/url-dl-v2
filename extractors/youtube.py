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
    "https://youtu.be/g2Y69HPXiqU",
    "https://www.youtube.com/watch?v=72-ebRSMJdE&t=2442s",
    "https://music.youtube.com/watch?v=okt6g5nlvIs&list=RDAOQfKGzjsUG2vYFjtBNNLahw",
    "https://www.youtube.com/playlist?list=PL7Rm1eEDbAx0CFWAL9oBTEY3qaSTVNGzn",
    "https://www.youtube.com/channel/UC94Z4HZJkhPm94YPH1GE3bw",
    "https://youtu.be/XqG9DC6ajFg",
    "https://youtu.be/jOpzP33_USs",
    "https://youtu.be/sbe1JYjLbJI",
    "https://youtu.be/HLGdD1O7R7g",
    "https://youtu.be/qjtfrX3iMIU",
    "https://youtu.be/aXnFa9PHC0A" 
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

def youtube_extractor(Downloader):
    global dl_object
    dl_object = Downloader.objects_list[Downloader.current]
    dl_object.site = "youtube"
    data = dl_object.data
    data["sub_objects"] = []
    def check_type(url):
        def set_youtube_type(a):
            data["type"] = a #May change type

        if re.search(r'https://music.youtube',url):
            set_youtube_type("music")
        elif re.search(r'https://www.youtube.com/channel',url):
            set_youtube_type("channel")
        elif re.search(r'https://www.youtube.com/playlist',url):
            set_youtube_type("playlist")
        else:
            set_youtube_type("video")

    def extract_video_id(url):
        if len(url) == 11:
            return url        
        elif re.search(r'(https).*(youtu.be).*',url) != None:
            return re.search(r'(?<=https://youtu.be/).{11}',url).group()
        elif re.search(r'(https://www.youtube.com/watch)',url) != None:
            return re.search(r'(?<=https://www.youtube.com/watch\?v=).{11}',url).group()

    check_type(data["url"])

    if data["type"] == "playlist":
        a_prev = ""
        for a in re.findall(r'(?<=videoId":").{11}',utils.source_code(data['url'])):
            
            if a != a_prev:
                data["sub_objects"].append({"id":a})
                a_prev = a
        del a_prev
        data["playlist_length"] = len(data["sub_objects"])

    elif data["type"] == "channel":
        #Channel stuff
        pass
    elif data["type"] == "music":
        pass
    else:
        data["sub_objects"].append({"id":extract_video_id(data['url'])})

    for sub_object in data["sub_objects"]:
        try:
            sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
        except:
            utils.give_it_some_time()
            try:
                sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
            except:
                try:
                    sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
                except:
                    try:
                        sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
                    except:
                        utils.give_it_some_time()
                        sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
        #DEBUG
        print(sub_object["id"])
    
    download_handler(Downloader)
    return Downloader
    #print(utils.print_json(data))

def extract_video_info(yt_id):

    url = "https://youtu.be/"+yt_id

    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text,'lxml')
    test = soup.find(attrs = {"class":"skeleton flexy","id":"player"}).next_element.next_element.contents[5].string
    test = re.search(r'(?<=player_response":").*(?="}};ytplayer.web_player_context_config)',test, re.DOTALL).group()
    utils.file_write("Test_1.txt",test)
    test = utils.string_escape(test)
    utils.file_write("Test_2.txt",test)
    test = json.loads(test)
        
    streams = []
    ytformats = test["streamingData"]["adaptiveFormats"]
    for i,a in enumerate(ytformats):
        stream_type = a["mimeType"][:a["mimeType"].find("/")]
        file_type = a["mimeType"][len(stream_type)+1:a["mimeType"].find("; ")]
        try:
            url = a["url"]
            s=None
        except KeyError: #Just copied from https://i.stack.imgur.com/gwsZg.jpg
            url = a["signatureCipher"]

        if stream_type == "audio":
            bitrate_actual = int(a["bitrate"])
            if bitrate_actual < 144000:
                bitrate = 128
            elif bitrate_actual >= 144000:
                bitrate = 160
            else:
                bitrate = int(bitrate_actual/1000)

            if file_type == "mp4":
                file_type = "m4a"

            stream_name = "{}_{}_{}".format(stream_type,bitrate,file_type)

        elif stream_type == "video":
            quality = a["qualityLabel"]
            resolution = (a["width"],a["height"])

            stream_name = "{}_{}_{}".format(stream_type,quality,file_type)
        
        streams.append({})
        streams[i]["name"] = stream_name
        streams[i]["url"] = url
        streams[i]["stream_type"] = stream_type
        streams[i]["file_type"] = file_type
        try:
            streams[i]["bitrate"] = bitrate
        except:
            streams[i]["quality"] = quality
            streams[i]["resolution"] = resolution

    foo = test["microformat"]["playerMicroformatRenderer"]
    video_info = {}
    video_info["description"] = foo["description"]["simpleText"]
    try:
        video_info["category"] = foo["category"]
    except:
        video_info["category"] = ""
    video_info["channel id"] = foo["externalChannelId"]
    video_info["length"] = foo["lengthSeconds"]
    video_info["channel"] = foo["ownerChannelName"]
    video_info["publish date"] = foo["publishDate"]
    video_info["thumbnail url"] = foo["thumbnail"]["thumbnails"][0]["url"]
    video_info["title"] = foo["title"]["simpleText"]
    video_info["views"] = foo["viewCount"]

    return video_info, streams
    
    #test = json.dumps(test, indent=4, sort_keys=True)

    #utils.file_write("Test_4.txt",test)
    
def download_handler(Downloader):
    dl_object = Downloader.objects_list[Downloader.current]
    for sub_object in dl_object.data["sub_objects"]:
        video_info = sub_object["video_info"]

        root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"youtube",video_info["title"])
        dl_object.download_info.append(root_download_dir)

        streams = sub_object["streams"]

        video_stream = get_best_video(streams)
        audio_stream = get_best_audio(streams)
        
        info_string = """{}

Channel: {}
Channel ID: {}
Category: {}
Views: {}
Publish Date: {}
Length: {} seconds
Description:

{}

Streams downloaded: {}, {}
        """.format(
            video_info["title"],
            video_info["channel"],
            video_info["channel id"],
            video_info["category"],
            video_info["views"],
            video_info["publish date"],
            video_info["length"],
            video_info["description"],
            video_stream["name"], audio_stream["name"]
        )

        #Text File
        dl_object.download_info.append({
            "path":(os.path.join(root_download_dir,"Info.txt")),
            "text file": True,
            "download": False,
            "contents": info_string,
            "thumbnail": None,
            "merge audio": None
        })
        #audio file
        if audio_stream["url"].startswith("http") == True:
            audio_filename = "video_"+utils.apostrophe(video_info["title"])+"."+audio_stream["file_type"]
            dl_object.download_info.append({
                "path":(os.path.join(root_download_dir,audio_filename)),
                "text file": False,
                "download": True,
                "contents": audio_stream["url"],
                "thumbnail": video_info["thumbnail url"],
                "merge audio": None
            })
        else:
            print("Audio stream undownloadable") #log some form of error
        #Video File
        if video_stream["url"].startswith("http") == True:
            video_filename = "audio_"+utils.apostrophe(video_info["title"])+"."+audio_stream["file_type"]
            dl_object.download_info.append({
                "path":(os.path.join(root_download_dir,video_filename)),
                "text file": True,
                "download": True,
                "contents": video_stream["url"],
                "thumbnail": None,
                "merge audio": (os.path.join(root_download_dir,audio_filename))
            })
        else:
            print("Video stream undownloadable")#log some form of error

def get_best_audio(streams, *selected_type):
    highest = 0
    final_stream = None
    for a in streams:
        if a["stream_type"] == "audio":
            if a['bitrate'] > highest:
                if selected_type == ():
                    highest = a['bitrate']
                    final_stream = a
                else:
                    if a['file_type'] == selected_type[0]:
                        highest = a['bitrate']
                        final_stream = a
    if final_stream != None:
        return final_stream
    else:
        print("No audio stream found")

def get_best_video(streams,*selected_type):
    
    highest = 0
    final_stream = None
    for a in streams:
        if a['stream_type'] == "video":
            if a['resolution'][1] > highest:
                if selected_type == ():
                    highest = a['resolution'][1]
                    final_stream = a
                else:
                    if a['file_type'] == selected_type[0]:
                        highest = a['resolution'][1]
                        final_stream = a
    if final_stream != None:
        
        return final_stream
    else:
        print("No video stream found")

if __name__ == "__main__":
    
    Downloader = extractor_test_setup()
    for i in range(len(test_links)):
        Downloader.current = i
        youtube_extractor(Downloader)