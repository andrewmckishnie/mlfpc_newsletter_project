import imaplib
import email
from email.header import decode_header
import re
import time
import requests as req
from imap_tools import MailBox, AND

###### CAPWORDS Helper function
####### Creates proper capitalization patterns for topics and sources by
####### capitalizing the first letter of every word, accounting for exceptions
####### in both directions

def capwords(words):
    always_lower_words = ['a', 'an', 'and', 'the', 'or']
    always_upper_words = ['BIPOC']
    words_split = words.split()
    initial_word = words_split[0].upper() if words_split[0].upper() in always_upper_words else words_split[0].capitalize()
    words_split.remove(words_split[0])
    if len(words_split) != 0:
        words_cap = [word.lower() if word.lower() in always_lower_words else word.upper() if word.upper() in always_upper_words else word.capitalize() for word in words_split]
        non_initial_words = ' '.join(words_cap)
        processed_words = initial_word + ' ' + non_initial_words
    else:
        processed_words = initial_word
    return processed_words


####### PROCESS SUBJECT helper function
####### takes in the subject from an email,
####### processes and extracts the relevant
####### information which is returned in a dictionary



def process_subject(subject):
    subject = re.sub('\n', "", subject)
    subject = re.sub('  ', ' ', subject)
    subject = re.sub('\r', '', subject)
    subject = re.sub('[}{]', '', subject)
    src_pattern = 'NL:MLFPC:(.*?):'
    date_pattern = 'NL:MLFPC:.*?:(.*?):'
    topic_1_pattern = 'NL:MLFPC:.*?:.*?:(.*?):'
    topic_2_pattern = 'NL:MLFPC:.*?:.*?:.*?:(.*?):'
    topic_3_pattern = 'NL:MLFPC:.*?:.*?:.*?:.*?:(.*?):'
    topic_4_pattern = 'NL:MLFPC:.*?:.*?:.*?:.*?:.*?:(.*?):'
    topic_5_pattern = 'NL:MLFPC:.*?:.*?:.*?:.*?:.*?:.*?:(.*?):'
    source = re.findall(src_pattern, subject)
    date_ = re.findall(date_pattern, subject)
    topic_1 = re.findall(topic_1_pattern, subject)
    topic_2 = re.findall(topic_2_pattern, subject)
    topic_3 = re.findall(topic_3_pattern, subject)
    topic_4 = re.findall(topic_4_pattern, subject)
    topic_5 = re.findall(topic_5_pattern, subject)
    src = capwords(source[0])
    dat = capwords(date_[0])
    top_1 = capwords(topic_1[0])
    if topic_2:
        top_2 = capwords(topic_2[0])
        if topic_3:
            top_3 = capwords(topic_3[0])
            if topic_4:
                top_4 = capwords(topic_4[0])
                if topic_5:
                    top_5 = capwords(topic_5[0])
                else:
                    top_5 = 'N/A'
            else:
                top_4 = 'N/A'
                top_5 = 'N/A'
        else:
            top_3 = 'N/A'
            top_4 = 'N/A'
            top_5 = 'N/A'

    else:
        top_2 = 'N/A'
        top_3 = 'N/A'
        top_4 = 'N/A'
        top_5 = 'N/A'

    newsletter_dict = {}
    newsletter_dict["Source"] = src
    newsletter_dict["Date"] = dat
    newsletter_dict["Topic_1"] = top_1
    newsletter_dict["Topic_2"] = top_2
    newsletter_dict["Topic_3"] = top_3
    newsletter_dict["Topic_4"] = top_4
    newsletter_dict["Topic_5"] = top_5


    return newsletter_dict

####### EXTRACT URL helper function
####### takes in body of email
####### returns url of newsletter
def extract_url(body):
    link_pattern = 'href="(.*?)".*?>View'
    link = re.findall(link_pattern, body)
    url = link[0]
    url = re.sub('&amp;', 'AMPERSAND', url)
    url = re.sub('&', 'AMPERSAND', url)

    return url

####### GET NEWSLETTERS helper function
####### takes in username and password, extracts
####### newsletters from email and processes emails
####### to return a list of dictionaries composed of
####### newsletters' entry information


def get_newsletters(username, password):

    newsletters_list = list()
    emails_to_move = list()
    with MailBox('imap.gmail.com').login(username, password, 'INBOX') as mailbox:
        messages = list(mailbox.fetch(AND(subject='NL:MLFPC')))
        print("--------")
        print("There are "+str(len(messages))+" new newsletters")
        print("--------")
        for msg in messages:
            subject = msg.subject
            if subject[0:8].upper() == 'NL:MLFPC':
                body = msg.html
                msg_id = msg.uid
                url = extract_url(body)
                newsletter = process_subject(subject)
                newsletter["URL"] = url
                newsletters_list.append(newsletter)
                emails_to_move.append(msg_id)

        for id in emails_to_move:
            mailbox.move(mailbox.fetch(AND(uid=id)), 'Processed')


    return newsletters_list

###### SEND NEWSLETTERS helper function
###### takes in list of dictionaries, processes these
###### into a set of get parameters and sends get request
###### to the appropriate page, where the PHP server
###### inserts info into database

def send_newsletters(newsletters_list):
    x = 0
    for nl_dict in newsletters_list:
        get_params = ""
        nl_key = ""
        dict_items = nl_dict.items()
        for key,value in dict_items:
            get_params += key + "=" +value + "&"
        get_params += nl_key
        url = "https://mlfpc.ca/newsletter_db_add"
        r = req.get(url, get_params)
        print("-----")
        print(r)
        print(get_params)
        print('-----')
        x += 1
        time.sleep(3)
    return x
