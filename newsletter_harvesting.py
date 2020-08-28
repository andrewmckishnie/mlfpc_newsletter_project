import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import re
import newsletter_utils
import mysql.connector
from mysql.connector import Error
    
def harvest_newsletters():
    
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
                cursor.execute('''SELECT * FROM topics''')
                topics_fetched = cursor.fetchall()
                topics_dict = {}
                for entry in topics_fetched:
                    topics_dict[entry[1]] = entry[0]
                top_1_id = topics_dict[top_1]
                top_2_id = topics_dict[top_2]
                top_3_id = topics_dict[top_3]
                top_4_id = topics_dict[top_4]
                top_5_id = topics_dict[top_5]
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


harvest_newsletters()

