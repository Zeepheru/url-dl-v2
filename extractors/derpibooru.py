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

#WIP