import sys
import re

def tester(): #for all extractors
    from os import getcwd #may have to open the folder in VSC to get correct working directory (otherwise is [:-11])
    sys.path.append(getcwd()) #needed for testing only

if __name__ == "__main__":
    tester()

import dl_utils as utils
import settings
import dl_object_init as dl

test_links = [
    "https://youtu.be/g2Y69HPXiqU",
    "https://www.youtube.com/watch?v=72-ebRSMJdE&t=2442s",
    "https://music.youtube.com/watch?v=okt6g5nlvIs&list=RDAOQfKGzjsUG2vYFjtBNNLahw",
    "https://www.youtube.com/playlist?list=PLJV1h9xQ7Hx97xa4PuilJTJ3sgh3SnryT",
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
    dl_object = Downloader.objects_list[Downloader.current]
    def check_type(url):
        def set_youtube_type(a):
            dl_object.data["type"] = a #May change type

        if re.search(r'https://music.youtube',url):
            set_youtube_type("music")
        elif re.search(r'https://www.youtube.com/channel',url):
            set_youtube_type("channel")
        elif re.search(r'https://www.youtube.com/playlist',url):
            set_youtube_type("playlist")
        else:
            set_youtube_type("video")

    check_type(dl_object.data["url"])
    #Then do stufffffffffffffffffffffffffffffffffffffffffffffffffff

if __name__ == "__main__":
    Downloader = extractor_test_setup()
    for i in range(len(test_links)):
        Downloader.current = i
        youtube_extractor(Downloader)