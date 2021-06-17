import sys
import re

from bs4 import BeautifulSoup
import requests
import json
import os

def dump_json(data):
    return json.dumps(data, indent=4, sort_keys=True)

def return_time_from_seconds(t):
    hrs = int(t / 3600)
    t = t % 3600 
    mins = int(t / 60)
    t = t % 60
    secs = t
    return "{}:{}:{:.03f}".format(hrs, mins, secs)

testingheaders = [
			{
				"name": "Accept",
				"value": "application/vnd.twitchtv.v5+json; charset=UTF-8"
			},
			{
				"name": "Accept-Encoding",
				"value": "gzip, deflate, br"
			},
			{
				"name": "Accept-Language",
				"value": "en-us"
			},
			{
				"name": "Authorization",
				"value": "OAuth zaji80e38pqna5lxend4fswhobqfv8"
			},
			{
				"name": "Client-ID",
				"value": "kimne78kx3ncx6brgo4mv6wki5h1ko"
			},
			{
				"name": "Connection",
				"value": "keep-alive"
			},
			{
				"name": "Content-Type",
				"value": "application/json; charset=UTF-8"
			},
			{
				"name": "DNT",
				"value": "1"
			},
			{
				"name": "Host",
				"value": "api.twitch.tv"
			},
			{
				"name": "Origin",
				"value": "https://www.twitch.tv"
			},
			{
				"name": "Referer",
				"value": "https://www.twitch.tv/"
			},
			{
				"name": "TE",
				"value": "Trailers"
			},
			{
				"name": "Twitch-Api-Token",
				"value": "e18e0c9a898b36cb344f7001b7150f89"
			},
			{
				"name": "User-Agent",
				"value": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
			},
			{
				"name": "X-Device-Id",
				"value": "N5PZ3f6x9sLBnnLpgzrEv2s3OMUHAhe3"
			},
			{
				"name": "X-Requested-With",
				"value": "XMLHttpRequest"
			}
        ]

def makeHeadersADick(listitem):
    the_header_dict = {}
    for a in listitem:
        the_header_dict[a["name"]] = a["value"]

    return the_header_dict

"""
Example of comment
{
    "_id": "1ff241ef-b831-4bf2-8a24-f870c3c55dac",
    "channel_id": "103192154",
    "commenter": {
        "_id": "84742174",
        "bio": null,
        "created_at": "2015-03-08T19:42:50.642752Z",
        "display_name": "FlurryDoesStuff",
        "logo": "https://static-cdn.jtvnw.net/jtv_user_pictures/242b8f55-283a-4aa5-b5d9-6927d4e69181-profile_image-300x300.png",
        "name": "flurrydoesstuff",
        "type": "user",
        "updated_at": "2021-06-12T19:40:54.086011Z"
    },
    "content_id": "1054127644",
    "content_offset_seconds": 11628.977,
    "content_type": "video",
    "created_at": "2021-06-12T20:55:56.677Z",
    "message": {
        "bits_spent": 100,
        "body": "Cheer100 Boy, you need to eat and drink and sober up a bit. You don't have to go to bed, or even end the stream, but for hecks sake, eat something",
        "fragments": [
            {
                "text": "Cheer100 Boy, you need to eat and drink and sober up a bit. You don't have to go to bed, or even end the stream, but for hecks sake, eat something"
            }
        ],
        "is_action": false,
        "user_badges": [
            {
                "_id": "predictions",
                "version": "blue-1"
            },
            {
                "_id": "subscriber",
                "version": "3009"
            },
            {
                "_id": "bits-leader",
                "version": "3"
            }
        ],
        "user_color": "#404A82",
        "user_notice_params": {}
    },
    "source": "chat",
    "state": "published",
    "updated_at": "2021-06-12T20:55:56.677Z"
}
"""

def parseComments(comments, simple=True, addTime=True, badges=False):
    ctexts = ""
    for c in comments:
        ctext = ""
        if simple:
            # display name of commenter
            ctext += c["commenter"]["display_name"]

            if addTime:
                # time of comment (relative to video)
                ctext += "\n" + return_time_from_seconds(c["content_offset_seconds"])

            if "\nbits_spent" in c["message"]:
                # bits
                ctext += "\n[{} bits]".format(c["message"]["bits_spent"])

            ## message text
            ctext += "\n" + c["message"]["body"]

        ctext += "\n\n"
        ctexts += ctext

    return ctexts

def getComments(videoId):
    s = requests.Session()
    
    headers = makeHeadersADick(testingheaders)
    ## get the headers from the top.

    offset, i = 0, 0
    prev_posturl = "stackoverflow.com"
    allcomments = []
    comment_n = 0
    # Hope a float works # yes they do.
    while True:

        posturl = "https://api.twitch.tv/v5/videos/{}/comments?content_offset_seconds={}".format(
            videoId, offset
        )
        if prev_posturl == posturl:
            # repeat preventer.
            break

        prev_posturl = str(posturl)
        # 

        print(posturl, end=" | ")
        r = s.get(posturl, headers=headers)
        # FUCK ME I AM SOOO DUMB
        # GET and POST fml
        ## YOU CAN LITERALLY SEE IT

        if r.status_code == 400:
            ## end of stream chat for ya
            break

        elif r.status_code != 200:
            print(r.status_code)

        thesecomments = json.loads(r.text)["comments"]
        # indiv comment list for the specific url
        ### next offset
        offset = thesecomments[-1]["content_offset_seconds"]

        #print(offset, end=" | ")
        print(len(thesecomments))
        comment_n += len(thesecomments)
        # for info....

        allcomments += thesecomments
        ## add to main list

        i += 1 # iterator  

        if i == 1024:
            # too long lmao. also failsafe.
            break  

    #print("Total Comments: " + str(comment_n))
    ## Numbers match up.

    return allcomments

def main(jsonOut=True, textOut=True):
    videoId = 1054127644
     # drunk stream

    allcommentsA = getComments(videoId)
    allcomments = []
    [allcomments.append(comment) for comment in allcommentsA if comment not in allcomments]
    # list comprehension to remove duplicates, apparently its pretty fast as well

    print("Total chat length: {}".format(len(allcomments)))
    ctext = parseComments(allcomments)


    # outputs as specific files in extractors.
    if jsonOut:
        outputPath = os.path.join("extractors", "twitch_chat_N{}.{}".format(videoId, "json"))

        with open(outputPath, "w", encoding="utf-8") as f:    
            f.write(dump_json(allcomments))

    if textOut:
        outputPath = os.path.join("extractors", "twitch_chat_N{}.{}".format(videoId, "txt"))

        with open(outputPath, "w", encoding="utf-8") as f: 
            f.write(ctext)

    print("Done with chat for Twtich VOD: {}.".format(videoId))

    #print(ctext)

if __name__ == "__main__":
    main()
