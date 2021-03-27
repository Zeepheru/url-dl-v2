#pip install --upgrade google-api-python-client
#pip install --upgrade google-auth-oauthlib google-auth-httplib2
#pip install --upgrade flask

#TESTING ONLY

import os

import flask

os.chdir(r"C:\Utilities\Scripts\url-dl-v2\extractors")

# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey="AIzaSyB7q5HYJfFt1ctb5wcIZVn7_YGygQj7yGA") #No need for OAuth 2.0 Authentication jeez I was so damn tired.

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id="UCfVgJvRCqS7nW1xP05Qjc9w"
    )
    response = request.execute()

    print(response)

if __name__ == "__main__":
    main()