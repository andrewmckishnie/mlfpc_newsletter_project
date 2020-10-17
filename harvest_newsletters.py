#!/usr/bin/env python

import imaplib
import email
from email.header import decode_header
import re
import time
import requests as req
from newsletter_utils import *
from datetime import datetime

username = ""
password = ""

def harvest_newsletters(username, password):

    today = datetime.now()
    current_date = today.strftime('%B %d, %Y')
    current_time = today.strftime('%H:%M:%S')

    print("--------------")
    print(f"Checking for newsletters at {current_time} on {current_date}")
    print("--------------")

    newsletters_list = get_newsletters(username, password)

    num_newsletters_sent = send_newsletters(newsletters_list)

    if num_newsletters_sent == 0:
        print("No new newsletters today")
    elif num_newsletters_sent == 1:
        print("Success! 1 newsletter sent")
    else:
        print(f"Success! {num_newsletters_sent} newsletters sent")

harvest_newsletters(username, password)
