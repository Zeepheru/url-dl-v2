import re
from resources.dl_items import i

def file_write(path,text):
    with open(path,'w', encoding = 'utf-8') as f:
        f.write(text)