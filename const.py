# coding:utf-8

import os
import re
import sys
import locale
from datetime import datetime
import requests

# info
DEVELOPMENT = False
__version__ = 0.2
PROJECT_NAME="OpusED"

# File Name
date=datetime.now().strftime('%Y%m%d%H%M%S')
LOG_FILE_PATH='./log/'
LOG_FILE_NAME=LOG_FILE_PATH+date+"_log.txt"
IN_FILE_NAME='in.txt'

if not os.path.isdir(LOG_FILE_PATH): os.mkdir(LOG_FILE_PATH)

# thread
THREAD_CNT=30
WAIT_OTHER_THREAD=True

# var
RETRY_CNT=3
RETRY_DELAY=10
