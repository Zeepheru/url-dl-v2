from tqdm import tqdm
import json
import os
import re
import requests

url = "https://www.theponyarchive.com/archive/recursivedir.txt"

r = requests.get(url, stream=True)

total_size = int(r.headers.get('content-length', 0))

block_size = 1024 #1 Kibibyte

t=tqdm(total=total_size, unit='iB', unit_scale=True)  #Solved by running in python(w).exe via task scheduler

with open("output.txt", 'wb') as f:
    for data in r.iter_content(block_size):
        t.update(len(data))
        f.write(data)
t.close()