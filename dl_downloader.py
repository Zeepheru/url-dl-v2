from tqdm import tqdm
import json
import os
import re
import requests
import dl_utils as utils
import dl_object_init as dl
import urllib
import ffmpeg
import shutil

import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import EasyMP3
from mutagen.id3 import ID3, APIC

import eyed3

from PIL import Image

import dl_logger as dl_logger

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
    try:
        new["date"] = str(download_object["metadata"]["year"])
    except:
        # some downloads may not have year / date metadata
        pass

    new.save()

def createallfolders(filepath):
    if "\\" in filepath:
        only_folders = re.search(r".*(?=\\)", filepath).group()

        if not os.path.exists(only_folders):
            if "\\" not in only_folders:
                current_folder = only_folders
                if not os.path.exists(current_folder):
                    os.mkdir(current_folder)

            else:
                all_folders = re.findall(r'^.*?(?=\\)|(?<=\\).*?(?=\\)|(?<=\\).+$',only_folders)
                current_folder = only_folders

                for folder in all_folders:
                    current_folder = os.path.join(current_folder,folder)
                    if not os.path.exists(current_folder):
                        #print("CREATING "+current_folder)
                        os.mkdir(utils.remove_periods_from_end(current_folder))

def mp3_apply_image(url, audio_path):
    dl_logger.log_to_file("Applying mp3 cover")
    # album art. 
    # https://www.programcreek.com/python/example/63462/mutagen.mp3.EasyMP3
    # Thanks Internet

    audio = EasyMP3(audio_path, ID3=ID3)

    img = urllib.request.urlopen(url)

    audio.tags.add(
        APIC(
            encoding=3,  # UTF-8
            mime=url,
            type=3,  # 3 is for album art
            desc='Cover',
            data=img.read()  # Reads and adds album art
        )
    )
    audio.save()

def mp3_apply_image_local(imgpath, audio_path):
    dl_logger.log_to_file("Applying mp3 cover")

    audiofile = eyed3.load(audio_path)
    if audiofile.tag == None:
        audiofile.initTag() #wipes???

    audiofile.tag.images.set(3, open(imgpath,'rb').read(), 'image/png')

    audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
    print("YES")

def create_download_json(Downloader):
    current = Downloader.objects_list[Downloader.current]
    dl_logger.log_to_file("Creating download information json.")
    if current.site == "Youtube":
        if current.data["type"] == "channel":
            # changed data to current lol
            filename = "{}_channel_{}_{}.json".format(current.site, current["channel name"], re.search(utils.parent_dir_regex,current.download_info[0]).group()) #data undefined????

        elif current.data["type"] == "playlist":
            filename = "{}_playlist_{}_{}.json".format(current.site, current["playlist name"], re.search(utils.parent_dir_regex,current.download_info[0]).group())

        else:
            filename = "{}_{}.json".format(current.site, re.search(r'.*(?=\.)',current.download_info[-1]["filename"]).group())
    else:
        filename = "{}_{}.json".format(current.site, re.search(r'.*(?=\.)',current.download_info[-1]["filename"]).group())
        
    try:
        filename = filename.replace("_video_","_")
    except:
        pass

    if not os.path.exists((os.path.join(Downloader.settings["directories"]["json"],filename))):
        with open (os.path.join(Downloader.settings["directories"]["json"],filename),'w', encoding = 'utf-8') as f:
            f.write(utils.dump_json(current.download_info))

def file_download_handler(download_object, Downloader):
    if isinstance(download_object, dict):
        output_path = download_object["path"]
        
        #recheck just in case, also double path error check
        parent_dir = re.search(utils.parent_dir_regex,download_object["path"]).group()
        if os.path.exists(parent_dir) != True: 
            createallfolders(parent_dir)
            if os.path.exists(parent_dir) != True: 
                os.mkdir(parent_dir) #paranoia lol
            dl_logger.log_to_file("Created directory: {}".format(parent_dir))

        url = download_object["contents"]
        if url != "http_mergeonly":
            if download_object["text file"] == True:
                utils.file_write(output_path,url)
                dl_logger.log_to_file("Writing text file.")

            if Downloader.settings["debug"]["print download info"] == True:
                print(utils.print_json(download_object))

            if Downloader.settings["debug"]["download"] == True and download_object["download"] == True:
                try:
                    dl_logger.log_info("Downloading: {}".format(r""+download_object["filename"]))
                except:
                    dl_logger.log_info("Downloading to: {}".format(r""+output_path)) #CHange this print statement
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

                if re.search(r'.mp3',output_path) != None: 
                    applymetadata(download_object)

        
        K = None
        try:
            download_object["merge audio"]
            if download_object["merge audio"] != None:
                K = True
            else:
                k = False
        except:
            k = False

        if Downloader.settings["debug"]["download"] == True:
            if K:
                merge_streams(download_object)
                os.chdir(Downloader.settings["directories"]["main"]) #might now be broken.

            if download_object["path"][-3:] == "mp3":
                # moved here so its no longer overwritten.
                try:
                    mp3_apply_image(download_object["thumbnail"], download_object["path"])
                except Exception as e:
                    dl_logger.log_info(e)
                    dl_logger.log_to_file(e)

def download(Downloader):
    if Downloader.objects_list[Downloader.current].site == "youtube" or Downloader.objects_list[Downloader.current].site == "bandcamp":
        folder_path = Downloader.objects_list[Downloader.current].download_info[0]
        if isinstance(folder_path, str) == True: #only if a folder is required is the download_info[0] a string being the download folder.
            if os.path.exists(folder_path) != True: 
                os.mkdir(folder_path)
                try:
                    try:
                        dl_logger.log_to_file(r"Created directory: "+utils.string_escape_path(r""+folder_path))
                    except:
                        print(r"Unable to log ----> Created directory: "+utils.
                        string_escape_path(r""+folder_path))
                except:
                    pass # I give up on this

    if Downloader.settings["debug"]["export download info"] == True:
        create_download_json(Downloader)
    for download_object in Downloader.objects_list[Downloader.current].download_info:
        file_download_handler(download_object, Downloader)

    return Downloader

def merge_streams(download_object): #seems like a YT exclusive, as always
    while True:
        folder_path = re.search(utils.parent_dir_regex,download_object["path"]).group()
        os.chdir(folder_path)

        ## now the code here goes through the listdir of the export folder and settles stuff out
        video_path, audio_path, thumbnail = "", "", ""
        for f in os.listdir(folder_path):
            if f.endswith(".png") or f.endswith(".jpg"):
                thumbnail = os.path.join(folder_path, f)
            elif f.startswith("tmpvideo_"):
                video_path = os.path.join(folder_path, f)
            elif f.startswith("tmpaudio_"):
                audio_path = os.path.join(folder_path, f)
        ###

        #checks if the audio and video files exist in the first place because uh they may not lol
        print(video_path)
        print(audio_path)
        if not os.path.isfile(video_path):
            dl_logger.log_to_file("Video file does not exist.")
            break
        elif not os.path.isfile(audio_path):
            dl_logger.log_to_file("Audio file does not exist.")
            break
        
        new_video_path = video_path.replace("tmpvideo_","temp_")
        if new_video_path[-4:] == 'webm':
            new_video_path = new_video_path.replace(".webm",".mp4") #force this, I'm very tired
        new_audio_path = audio_path.replace("tmpaudio_","")

        dl_logger.log_to_file("Merging audio and video files.")
        try:
            input_video = ffmpeg.input(video_path)
            input_audio = ffmpeg.input(audio_path)
            ffmpeg.output(input_audio.audio,input_video.video,new_video_path, shortest=None, vcodec='copy').run() 
            #I WANT TO AHHHHHHHHHHHHHHHHHHHBHHHHHHHHH - FileNotFoundError: [WinError 2] The system cannot find the file specified - does seem to be a Python x FFMPEG error not mine, but I have to fix it anyway lol yargjhhhhh

        except:
            #print("BACKUP1")
            #Backup if needed, unused on laptop as well
            os.system("ffmpeg -i {} -i {} -c:v copy -c:a aac {}".format(video_path,audio_path,new_video_path))

        #https://stackoverflow.com/questions/54717175/how-do-i-add-a-custom-thumbnail-to-a-mp4-file-using-ffmpeg

        #lets try this random bosh - dont complain for using two ffmpeg commands I am too lazy or dumb to combine them
        dl_logger.log_to_file("Adding thumbnail to video file.")
        new_new_video_path = new_video_path.replace("temp_","")
        try:
            #os.system(r'ffmpeg -i "temp_4everfreebrony - When Morning Is Come (feat. Namii).mp4" -i "Thumbnail.png" -map 1 -map 0 -c copy -disposition:0 attached_pic "4everfreebrony - When Morning Is Come (feat. Namii).mp4"') #WUT?
            os.system('ffmpeg -i "{}" -i "{}" -map 1 -map 0 -c copy -disposition:0 attached_pic "{}"'.format(new_video_path, thumbnail, new_new_video_path))
            #Shortened filepaths, chdir'd to the folder to use ffmpeg there seems to fix issues
        except: #no thumb or some stupid error
            shutil.copy(new_video_path, new_new_video_path)

        try:
            os.remove(video_path)
            #os.remove(new_video_path)
        except:
            pass

        if not os.path.isfile(new_audio_path):
            os.rename(audio_path,new_audio_path)
            
        #convert to mp3 for well? purposes.
        if new_audio_path[-4:] == 'webm' or new_audio_path[-3:] == 'm4a': #Youtube Checker removed, too lazy to fix it anyway so yeahhhhhhhhhh
            dl_logger.log_to_file("Coverting audio file to mp3.")
            temp_new_audio_path = new_audio_path + "I_AM_TOO_LAZY_TO_USE_REGEX"
            
            if ".webmI_AM_TOO_LAZY_TO_USE_REGEX" in temp_new_audio_path:
                new_new_audio_path = temp_new_audio_path.replace(".webmI_AM_TOO_LAZY_TO_USE_REGEX",".mp3")
            elif ".m4aI_AM_TOO_LAZY_TO_USE_REGEX" in temp_new_audio_path:
                new_new_audio_path = temp_new_audio_path.replace(".m4aI_AM_TOO_LAZY_TO_USE_REGEX",".mp3")

            try:
                convert_input = ffmpeg.input(new_audio_path)
                ffmpeg.output(convert_input.audio, new_new_audio_path, shortest=None, vcodec='copy').run()
            except:
                #print("BACKUP3")
                #Backup if needed, unused on laptop as well
                os.system("ffmpeg -i {} -acodec libmp3lame -ab 128k {}".format(new_audio_path, new_new_audio_path)) #128k bitrate temp 
                
            try:
                os.remove(new_audio_path)
            except:
                pass
        
        else:
            new_new_audio_path = new_audio_path
            
        dl_logger.log_to_file("Trying to apply metadata")
        mp3_apply_image_local(thumbnail, new_new_audio_path)
        applymetadata({
            "path": new_new_audio_path,
            "metadata": download_object["metadata"]
        })
        dl_logger.log_to_file("Applied Metadata.")

        #finally deletes all temp files, manually because I cant find the right fecking variables
        for f in os.listdir(folder_path):
            if f.startswith("TEMP_") or f.startswith("temp_"):
                os.remove(os.path.join(folder_path, f))

if __name__ == "__main__":
    def Tester_bandcamp_metadata():
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
                "track number":"track numero uno",
                "playlist":"playlist",
                "year":"2010"
                }
            }
        )
    #folder_path = r'C:\Utilities\Scripts\url-dl-v2 output\youtube\4everfreebrony - When Morning Is Come (feat. Namii)'
    def lol():
        merge_streams(
            {
            "contents": "https://r6---sn-nu5gi0c-npoee.googlevideo.com/videoplayback?expire=1607029746&ei=kv_IX6vWMZiV1Ab736OABw&ip=218.212.223.31&id=o-APbp8OXs1uFrPiF-alTq0J1Jb9EcGVZ0lyeZBIoVBirc&itag=137&aitags=133%2C134%2C135%2C136%2C137%2C160%2C242%2C243%2C244%2C247%2C248%2C278&source=youtube&requiressl=yes&mh=kv&mm=31%2C29&mn=sn-nu5gi0c-npoee%2Csn-npoeenle&ms=au%2Crdu&mv=m&mvi=6&pl=21&initcwndbps=1427500&vprv=1&mime=video%2Fmp4&ns=-hXEuKBaWUkw_PykKmnDm6kF&gir=yes&clen=8586824&dur=298.031&lmt=1531346674387950&mt=1607007172&fvip=5&keepalive=yes&c=WEB&n=TB-5HtTRS_wdVKQQt&sparams=expire%2Cei%2Cip%2Cid%2Caitags%2Csource%2Crequiressl%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRAIgMxPcHIFGU_jbCFRcfgLOh5I56ZpkTOeWGsLPU9qYhb8CIELGIS3jEovDNmCwFGRDFAuHjJgzzMYMntHfh5-Dx0Jr&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRgIhAOZzw0jLToBz_nNJSfqG-Ev5SkBGuoSNVYa4WlgkCzj6AiEA11VhgihnJ6taK3YNZtwy2ZeProwFUsntHve_ZFkb2pM%3D",
            "download": True,
            "merge audio": "C:\\Utilities\\Scripts\\url-dl-v2 output\\youtube\\4everfreebrony - When Morning Is Come (feat. Namii)\\audio_4everfreebrony - When Morning Is Come (feat. Namii).webm",
            "path": "C:\\Utilities\\Scripts\\url-dl-v2 output\\youtube\\4everfreebrony - When Morning Is Come (feat. Namii)\\video_4everfreebrony - When Morning Is Come (feat. Namii).mp4",
            "text file": True,
            "thumbnail": None
        }
        )