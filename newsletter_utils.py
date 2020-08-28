def capwords(words):
    always_lower_words = ['a', 'an', 'and', 'the', 'or']
    always_upper_words = ['BIPOC']
    words_s = words.split()
    init_word = words_s[0].upper() if words_s[0].upper() in always_upper_words else words_s[0].capitalize()
    words_s.remove(words_s[0])
    words_cap = [word.lower() if word.lower() in always_lower_words else word.upper() if word.upper() in always_upper_words else word.capitalize() for word in words_s]
    non_init_words = ' '.join(words_cap)
    if len non_init_words != 0:
        processed_words = init_word + ' ' + non_init_words
        return processed_words
    else:
        return init_word
    

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
