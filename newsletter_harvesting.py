import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import re
import mysql.connector
from mysql.connector import Error


def capwords(words):
    always_lower_words = ['a', 'an', 'and', 'the', 'or']
    always_upper_words = ['BIPOC']
    words_s = words.split()
    init_word = words_s[0].upper() if words_s[0].upper() in always_upper_words else words_s[0].capitalize()
    words_s.remove(words_s[0])
    words_cap = [word.lower() if word.lower() in always_lower_words else word.upper() if word.upper() in always_upper_words else word.capitalize() for word in words_s]
    non_init_words = ' '.join(words_cap)
    processed_words = init_word + ' ' + non_init_words
    return processed_words
    

def process_subject(subject):
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
                    print("Topic 5: ", top_5)
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
    return src, dat, top_1, top_2, top_3, top_4, top_5
                
    
    
    
def find_newsletters():
    
    username = ""
    password = ""
    
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(username, password)

    status, message = imap.select("INBOX")

    N = 10

    messages = int(message[0])
    
    if messages < N:
        N = messages
    
    
    newsletter_list = list()

    for i in range(messages, messages-N, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode()
                newsletter_check = subject[0:8].upper()
                if newsletter_check != 'NL:MLFPC':
                    continue
                print("We got one, yay!")
                src, dat, top_1, top_2, top_3, top_4, top_5 = process_subject(subject)
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))

                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

                link_pattern = 'href="(.*?)".*?>View'
                link = re.findall(link_pattern, body)
                newsletter_list.append((src, dat, top_1, top_2,top_3, top_4, top_5, link[0]))

    imap.close()
    imap.logout()

    print("Newsletters found:", newsletter_list)
    
    

    try:
        connection = mysql.connector.connect(host='',
                                             database='',
                                             port='3306',
                                             user='',
                                             password='')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor(buffered=True)
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)
            
            for newsletter in newsletter_list:
                src = newsletter[0]
                dat = newsletter[1]
                top_1 = newsletter[2]
                top_2 = newsletter[3]
                top_3 = newsletter[4]
                top_4 = newsletter[5]
                top_5 = newsletter[6]
                url = newsletter[7]
            
                cursor.execute('''SELECT * FROM newsletter_sources WHERE source_name = %s''' , (src,))
                src_id_fetch = cursor.fetchone()
                if src_id_fetch == None:
                    cursor.execute('''INSERT INTO newsletter_sources (source_name) VALUES (%s)''', (src,))
                    cursor.execute('''SELECT * FROM newsletter_sources WHERE source_name = %s''' , (src,))
                    src_id_fetch = cursor.fetchone()
                src_id = src_id_fetch[0]
                cursor.execute('''SELECT * FROM topics WHERE topic_name = %s''', (top_1, ))
                top_1_id = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM topics WHERE topic_name = %s''', (top_2, ))
                top_2_id = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM topics WHERE topic_name = %s''', (top_3, ))
                top_3_id = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM topics WHERE topic_name = %s''', (top_4, ))
                top_4_id = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM topics WHERE topic_name = %s''', (top_5, ))
                top_5_id = cursor.fetchone()[0]
                cursor.execute('''SELECT * FROM newsletters WHERE newsletter_url = %s''', (url,))
                url_fetch = cursor.fetchone()
                if url_fetch == None:
                    cursor.execute('''INSERT INTO newsletters (source_id, newsletter_url, newsletter_date, topic_1_id, topic_2_id, topic_3_id, topic_4_id, topic_5_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''', (src_id, url, dat, top_1_id, top_2_id, top_3_id, top_4_id, top_5_id, ))
                    connection.commit()  
                else:
                    continue
                

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if (connection.is_connected()):          
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


find_newsletters()

