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

import youtube_dl

#https://www.youtube.com/watch?v=X_TMtgjQuZI somehow is also ciphered, not even youtub-dl works.

test_links = [
    "https://www.youtube.com/channel/UCZIfhUoFkVPphEtnaZaGDqg",
    "https://www.youtube.com/channel/UC94Z4HZJkhPm94YPH1GE3bw",
    "https://youtu.be/g2Y69HPXiqU",
    "https://www.youtube.com/watch?v=72-ebRSMJdE&t=2442s",
    "https://music.youtube.com/watch?v=okt6g5nlvIs&list=RDAOQfKGzjsUG2vYFjtBNNLahw",
    "https://www.youtube.com/playlist?list=PL7Rm1eEDbAx0CFWAL9oBTEY3qaSTVNGzn",
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

def youtube_dl_backup(url,folder_path):
    dl_logger.log_info("Unable to use main Youtube Extractor, switching to Youtube-dl backend.")

    #audio
    def my_hook_audio(d):
        if d['status'] == 'finished':
            dl_logger.log_info('Done downloading audio.')

    ydl_opts_audio = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '256',
        }],
        'progress_hooks': [my_hook_audio],
        'outtmpl':os.path.join(folder_path,'%(title)s.%(ext)s')
    }
    with youtube_dl.YoutubeDL(ydl_opts_audio) as ydl:
        ydl.download([url])

    #video
    def my_hook_video(d):
        if d['status'] == 'finished':
            dl_logger.log_info('Done downloading audio.')

    ydl_opts_video = {
        'format': 'best',
        'progress_hooks': [my_hook_video],
        'outtmpl':os.path.join(folder_path,'%(title)s.%(ext)s')
    }
    with youtube_dl.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([url])

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
        elif re.search(r'https://www.youtube.com/channel',url) or re.search(r'https://www.youtube.com/c/',url):
            set_youtube_type("channel")
        elif re.search(r'https://www.youtube.com/playlist',url):
            set_youtube_type("playlist")
        else:
            set_youtube_type("video")

    def extract_video_id(url):
        if len(url) == 11:
            return url        
        elif re.search(r'=youtu.be&v=',url) != None:
            return re.search(r'(?<==youtu.be&v=).{11}',url).group()
        elif re.search(r'(https).*(youtu.be/).*',url) != None:
            return re.search(r'(?<=https://youtu.be/).{11}',url).group()
        elif re.search(r'(youtube.com/watch)',url) != None:
            return re.search(r'(?<=youtube.com/watch\?v=).{11}',url).group()

        
            
    check_type(data["url"])
    try:
        data["url"].replace(' ','')
    except:
        pass

    if data["type"] == "playlist":
        a_prev = ""
        for a in re.findall(r'(?<=videoId":").{11}',utils.source_code(data['url'])):
            
            if a != a_prev:
                data["sub_objects"].append({"id":a})
                a_prev = a
        del a_prev
        data["playlist_length"] = len(data["sub_objects"])

    elif data["type"] == "channel":
        if re.search(r'https://www.youtube.com/channel/|https://www.youtube.com/c/',data["url"]) != None:
            channel_url = data["url"]
        else:
            channel_url = "I DONT KNOW WHAT OTHER LINK YOU ARE GIVING ME"
        #main channel stuff.
        #Go look at Eilemonty for private videos that I cant settle

        response = requests.get(channel_url+"/about")
        response.raise_for_status()
        soup = BeautifulSoup(response.text,'lxml')
        #unfortunately I do not care about "about pages" sucks to be you -past me

        video_list_url = channel_url +"/videos"
        video_list_html = utils.source_code_b(video_list_url)
        a_prev = ""
        for a in re.findall(r'(?<=videoId":").{11}',video_list_html):
            
            if a != a_prev:
                data["sub_objects"].append({"id":a})
                a_prev = a
        del a_prev
        #Botch to get channel information from a video LOL
        channel_scrape = False
        list_of_ids = []
        for i in data["sub_objects"]:
            list_of_ids.append(i["id"])
            if channel_scrape != True:
                try:
                    video_info,shit = extract_video_info(i["id"])
                    del shit
                    #To get data
                    channel_scrape = True
                except:
                    pass
        data["channel name"] = video_info["channel"]
        data["channel image"] = video_info["channel image"]
        data["channel description"] = video_info["channel description"]
        channel_info_string = """Channel: {}
Channel URL: {}
Subscribers: NOT IMPLEMENTED
Description: 

{}

Downloaded IDs: 
{}

{}
""".format(
    data["channel name"],
    data["url"],
    data["channel description"],
    utils.dump_json(list_of_ids),
    utils.give_me_the_time()
)
        dl_info = Downloader.objects_list[Downloader.current].download_info
        dl_info.append(os.path.join(Downloader.settings["directories"]["output"],"youtube","channels",data["channel name"]))
        #text file
        dl_object.download_info.append({
            "filename":"Info.txt",
            "path":(os.path.join(os.path.join(Downloader.settings["directories"]["output"],"youtube","channels",data["channel name"]),data["channel name"]+" - Info.txt")),
            "text file": True,
            "download": False,
            "contents": channel_info_string,
            "thumbnail": None,
            "merge audio": None
        })
        #image
        dl_object.download_info.append({
            "filename":"Channel Image.png",
            "path":(os.path.join(os.path.join(Downloader.settings["directories"]["output"],"youtube","channels",data["channel name"]),"Channel Image.png")),
            "text file": False,
            "download": True,
            "contents": data["channel image"],
            "thumbnail": None,
            "merge audio": None
        })

        dl_logger.log_to_file("Channel has {} videos downloaded.".format(len(list_of_ids)))

    elif data["type"] == "music":
        pass #MAJSDJSADJSDSADKFSAHBKFCgdajshfkedsa jvfkhbdskfeg
    else:
        data["sub_objects"].append({"id":extract_video_id(data['url'])})
        

    for sub_object in data["sub_objects"]:
        dl_logger.log_info("Scraping for id: {}".format(sub_object["id"]))
        try:
            sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
        except:
            utils.give_it_some_time()
            try:
                sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])
            except:
                sub_object["video_info"], sub_object["streams"] = extract_video_info(sub_object["id"])

        #DEBUG
        #print(sub_object["id"])
    
    download_handler(Downloader)
    return Downloader
    #print(utils.print_json(data))

def extract_video_info(yt_id):
    url = "https://youtu.be/"+yt_id

    def scrape_yt_link(url):

        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text,'lxml')
        test = response.text
        #utils.file_write("Test_1.txt",test)
        
        #append extra regexes here for other html shenanigans 
        temp = re.search(r'(?<=player_response":").*|(?<=PlayerResponse = ).*|(?<=\["ytInitialPlayerResponse"\] = ).*',test).group()
        
        if temp[0:1] == '"':
            temp = temp [1:]
        if temp[0:1] == "{":
            temp = temp [1:]
        a = 1 #number of brackets
        for i in range(len(temp)):
            b = temp[i:i+1]
            if a != 0:
                if b == "{":
                    a += 1
                elif b == "}":
                    a = a-1
            elif a == 0:
                k = i
                break

        test = '{'+temp[0:k]
        if test.startswith(r'{\"') == True:
            test = utils.string_escape(test)
        #utils.file_write("Test_2.txt",test)
        #print("Json scraped")

        """For errors/random problems:
        should be finding:
        {"responseContext":{"serviceTrackingParams":[{"service":"GFEEDBACK","params":[{"key":"is_viewed_live","value":"False"},{"key":"logged_in","value":"0"},{"key":"e","value":"23970895,23932523,23970385,24590263,23942633,23963929,23857949,23942338,9407155,23969934,23884386,23839597,23882502,23976578,23804281,23946420,23948841,23972381,23911055,23969486,23972864,23918597,23976772,23973687,23968386,23951620,23973492,23944779,23890959,23961261,23744176,23934970,1714251,23965557,23940703,23958692,23973488,23970649,23978155,23973495,23961733,23970398,23973497,23735347,23970974"}]},{"service":"CSI","params":[{"key":"c","value":"WEB"},{"key":"cver","value":"2.20201202.08.00"},{"key":"yt_li","value":"0"},{"key":"GetPlayer_rid","value":"0x25485baf1f756f9c"}]},{"service":"GUIDED_HELP","params":[{"key":"logged_in","value":"0"}]},{"service":"ECATCHER","params":[{"key":"client.version","value":"2.20201202"},{"key":"client.name","value":"WEB"}]}],"webResponseContextExtensionData":{"hasDecorated":true}},"playabilityStatus":{"status":"OK","playableInEmbed":true,"miniplayer":{"miniplayerRenderer":{"playbackMode":"PLAYBACK_MODE_ALLOW"}},"contextParams":"Q0FFU0FnZ0I="},"streamingData":{"expiresInSeconds":"21540","formats":[{"itag":18,"url":"https://r2---sn-nu5gi0c-npoee.googlevideo.com/videoplayback?expire=1607088267\u0026ei=K-TJX_CJMrC73LUPx90n\u0026ip=218.212.223.31\u0026id=o-AIJ7tk6_fBnlj29Kes8FKX1MWBdOkNX1QVS49QVpzHVO\u0026itag=18"""
        #utils.file_write("Test_3.txt",utils.dump_json(test))
        #test = utils.string_escape(test) #Seems to be unnecessary
        #utils.file_write("Test_4.txt",test)
        #print("Parsing json.")
        try:
            test = json.loads(test) #Sometimes errors, best to just reload
        except Exception as e:
            dl_logger.log_exception(e)
            utils.file_write("Error json.txt",test)

        return test

    try:
        test = scrape_yt_link(url)
    except:
        try:
            test = scrape_yt_link(url)
        except:
            try:
                test = scrape_yt_link(url)
            except:
                test = scrape_yt_link(url)
        
    streams = []
    ytformats = test["streamingData"]["adaptiveFormats"]
    for i,a in enumerate(ytformats):
        stream_type = a["mimeType"][:a["mimeType"].find("/")]
        file_type = a["mimeType"][len(stream_type)+1:a["mimeType"].find("; ")]
        try:
            stream_url = utils.string_escape(a["url"])
            s=None
        except KeyError: #Just copied from https://i.stack.imgur.com/gwsZg.jpg
            stream_url = a["signatureCipher"]

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
        streams[i]["url"] = stream_url
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
    video_info["url"] = url
    video_info["channel id"] = foo["externalChannelId"]
    video_info["length"] = foo["lengthSeconds"]
    video_info["channel"] = foo["ownerChannelName"]
    video_info["publish date"] = foo["publishDate"]
    video_info["thumbnail url"] = foo["thumbnail"]["thumbnails"][0]["url"]
    video_info["title"] = foo["title"]["simpleText"]
    video_info["title"] = utils.apostrophe(video_info["title"])
    video_info["views"] = foo["viewCount"]
    try:
        random_variable_223 = test["endscreen"]["endscreenRenderer"]["elements"][0]["endscreenElementRenderer"]
        video_info["channel image"] = random_variable_223["image"]["thumbnails"][-1]["url"]
        #video_info["subscriber count"] = random_variable_223 - doesnt work lol (at least not there)
        video_info["channel description"] = random_variable_223["metadata"]["simpleText"]
        #src="https://yt3.ggpht.com/ytc/AAUvwnhDuaemX6BXptBi4KtxnVzhNaV6L97P3nKpXAgmJA=s48-c-k-c0xffffffff-no-rj-mo"
    except:
        video_info["channel image"] = "https://derpicdn.net/img/view/2012/10/14/122701__safe_artist-colon-inkwell_derpy+hooves_female_i+just+don%27t+know+what+went+wrong_mare_pegasus_pony_solo_technical+difficulties_wallpaper.jpg" #lol sorry in advance for this madness
        video_info["channel description"] = "unavailable"
        dl_logger.log_to_file('json["endscreen"]probably does not return anything. Recommended fix is to try the scrape again. Usually no problem unless its the first video link (For channels only).')

    for k in dict(video_info):
        video_info[k] = utils.string_escape(video_info[k])

    return video_info, streams
    
    #test = json.dumps(test, indent=4, sort_keys=True)

    #utils.file_write("Test_4.txt",test)
    
def download_handler(Downloader):
    dl_object = Downloader.objects_list[Downloader.current]
    for sub_object in dl_object.data["sub_objects"]:
        video_info = sub_object["video_info"]
        if dl_object.data["type"] == "channel":
            root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"youtube","channels",dl_object.data["channel name"],video_info["title"])
            #already appended
            #other Stuff for Download handler is in a seperate function
        else:
            root_download_dir = os.path.join(Downloader.settings["directories"]["output"],"youtube",utils.apostrophe(video_info["title"]))
            dl_object.download_info.append(root_download_dir)

        streams = sub_object["streams"]

        video_stream = get_best_video(streams)
        audio_stream = get_best_audio(streams)
        
        info_string = """{}

Video URL: {}
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
            video_info["url"],
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
            "filename":utils.apostrophe(video_info["title"])+" - Info.txt", #Better to organsise with the video name as well
            "path":(os.path.join(root_download_dir,video_info["title"]+" - Info.txt")),
            "text file": True,
            "download": False,
            "contents": info_string,
            "thumbnail": None,
            "merge audio": None
        })
        #Thumbnail - not sure if a forced png works
        dl_object.download_info.append({
            "filename":utils.apostrophe(video_info["title"])+" - Thumbnail.png",
            "path":(os.path.join(root_download_dir,video_info["title"]+" - Thumbnail.png")),
            "text file": False,
            "download": True,
            "contents": video_info["thumbnail url"],
            "thumbnail": None,
            "merge audio": None
        })
        #audio file
        if audio_stream["url"].startswith("http") == True:
            audio_filename = "audio_"+utils.apostrophe(video_info["title"])+"."+audio_stream["file_type"]
            dl_object.download_info.append({
                "filename":audio_filename,
                "path":(os.path.join(root_download_dir,audio_filename)),
                "text file": False,
                "download": True,
                "contents": audio_stream["url"],
                "thumbnail": video_info["thumbnail url"],
                "merge audio": None
            })
        else:
            dl_logger.log_info("! Video ({}|{}) undownloadable - cipher needed.".format(video_info["url"],video_info["title"])) #log some form of error
            
        #Video File
        if video_stream["url"].startswith("http") == True:
            video_filename = "video_"+utils.apostrophe(video_info["title"])+"."+video_stream["file_type"]
            dl_object.download_info.append({
                "filename":video_filename,
                "path":(os.path.join(root_download_dir,video_filename)),
                "text file": True,
                "download": True,
                "contents": video_stream["url"],
                "thumbnail": video_info["thumbnail url"],
                "merge audio": audio_filename,
                "metadata":{
                    "title":video_filename,
                    "artist":video_info["channel"],
                    "track number":0,
                    "playlist":"",
                    "year":re.search(utils.year_regex,video_info["publish date"]).group()
                }
            })
        else:
            pass #happens for both so yea
            #dl_logger.log_info("Video stream undownloadable (copyrighted music ftw")#log some form of error
            youtube_dl_backup(video_info["url"],root_download_dir)

    #utils.print_json(dl_object.download_info)

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
        dl_logger.log_info("No audio stream found")

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
        dl_logger.log_info("No video stream found")

if __name__ == "__main__":
    
    Downloader = extractor_test_setup()
    dl_logger.init_logger(Downloader.settings["directories"]["main"], "Youtube")
    for i in range(len(test_links)):
        Downloader.current = i
        youtube_extractor(Downloader)