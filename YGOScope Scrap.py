#!/usr/bin/env python
# coding: utf-8

# In[1]:


from urllib.request import urlopen
from bs4 import BeautifulSoup


# In[2]:


ygoscope_url = "https://www.ygoscope.com/explorer"

ygoscope_page = urlopen(ygoscope_url)
ygoscope_text = ygoscope_page.read().decode("utf-8")

ygoscope_soup = BeautifulSoup(ygoscope_text, "html.parser")

#print(ygoscope_soup.prettify())

match_cards_table = ygoscope_soup.find("table", id="match-cards-table")
#print(match_cards_table)

match_cards_body = match_cards_table.find("tbody")
#print(match_cards_body)

match_cards_rows = match_cards_body.find_all("tr")
#print(match_cards_rows)


# In[3]:


def sanitize(text):
    sanitized = text
    
    from_extra_deck = sanitized.find("\" from Extra Deck ")
    if from_extra_deck != -1:
        sanitized = sanitized[:from_extra_deck]
        
    return sanitized


# In[4]:


def convert_to_ban(appearance, ban_treshold, limit_treshold):
    if appearance > ban_treshold:
        return 0
    elif appearance > limit_treshold:
        return 1
    else:
        return 2


# In[5]:


most_used_cards_ygoscope = {}

for row in match_cards_rows:
    match_card_data = row.find_all("td")
    
    card_link = match_card_data[0].find("a")
    card_name = sanitize(card_link.text)
    card_appearance = match_card_data[1].text
    
    if most_used_cards_ygoscope.get(card_name) is None:
        most_used_cards_ygoscope[card_name] = int(card_appearance)
    else:
        most_used_cards_ygoscope[card_name] += int(card_appearance)
        #print(card_database[card_name])

#print(most_used_cards_ygoscope)


# In[6]:


i=1
title_collection = []
prompt = ""
api_limit = 50
for card in most_used_cards_ygoscope:
    prompt += card.replace(" ","_") + "|"
    
    i += 1
    if i > api_limit:
        title_collection.append(prompt[:-1])
        #print(prompt[:-1])
        #print()
        i = 1
        prompt = ""
        
title_collection.append(prompt[:-1])
#print(prompt[:-1])
#print()
#print(titles)


# In[7]:


import requests

most_used_cards = {}
for titles in title_collection:    

    S = requests.Session()

    URL = "https://yugipedia.com/api.php"

    PARAMS = {
        "action": "query",
        "prop": "revisions",
        "titles": titles,
        "rvprop": "content",
        "format": "json"
    }

    R = S.get(url=URL, params=PARAMS)
    print(R)
    data = R.json()

    #print(data)

    pages = data["query"]["pages"]
    #print(pages)

    for page in pages:
        card_name = pages[page]["title"]
        page_text = pages[page]["revisions"][0]["*"]
        #print(page_text)

        skip_alternate_password = page_text.rfind("alternate password")
        password_location = 0
        if skip_alternate_password == -1:
            password_location = page_text.find("password")
        else:
            password_location = page_text.find("password", skip_alternate_password+len("alternate password"))
            
        password_start = page_text.find("=", password_location)+1
        password_end = page_text.find("|", password_location)
        password = page_text[password_start:password_end].replace(" ", "").strip()

        card_appearance = most_used_cards_ygoscope[card_name]
        most_used_cards[password] = [convert_to_ban(card_appearance, 1000, 300), card_name]
        #most_used_cards[password] = [card_appearance, card_name]

print(most_used_cards)


# In[8]:


lfin_filename = "D:\\soft\\ProjectIgnis\\repositories\\lflists\\0TCG.lflist.conf"

lfin_file = open(lfin_filename, 'r')
lines = lfin_file.readlines()
#print(lines)

lf_data = {}

for line in lines:
    if line[0] == '#' or line[0] == '!':
        continue
    #print (line.strip())

    first_space = line.find(" ")
    second_space = line.find(" ", first_space+1)
    
    end_line = line.find("\t")
    if end_line == -1:
        end_line = second_space+1
        next_space = line.find(" ", end_line)
        while next_space != -1 and next_space > end_line:
            end_line = next_space+1
            next_space = line.find(" ", end_line)
    
        end_line = next_space        
    
    lf_data[line[:first_space]] = [int(line[first_space+1:second_space])
                                 , line[second_space+3:end_line]]
    
print (lf_data)


# In[9]:


lf_custom = lf_data.copy()

for card in most_used_cards:
    if lf_custom.get(card) is None:
        lf_custom[card] = most_used_cards[card]
    else:
        #print(most_used_cards[card][1])
        if lf_custom[card][0] > most_used_cards[card][0]:
            lf_custom[card][0] = most_used_cards[card][0]
            if lf_custom.get(str(int(card)-1)) is not None:
                lf_custom[str(int(card)-1)][0] = most_used_cards[card][0]     
            if lf_custom.get(str(int(card)+1)) is not None:
                lf_custom[str(int(card)+1)][0] = most_used_cards[card][0]

print (lf_custom)


# In[10]:


lfout_filename = "custom.lflist.conf"
lfout_file = open(lfout_filename, 'w')
lfout_file.writelines("!Custom\n")

for key in lf_data:
    line = key + " " + str(lf_custom.get(key)[0]) + " --" + lf_custom.get(key)[1] + "\n"
    lfout_file.writelines(line)

lfout_file.close()


# def find_password(card_name):
#     
#     yugipedia_url = "https://yugipedia.com/wiki/" + card_name.replace(" ", "_")
#     #print(yugipedia_url)
# 
#     yugipedia_page = urlopen(yugipedia_url)
#     yugipedia_text = yugipedia_page.read().decode("utf-8")
# 
#     yugipedia_soup = BeautifulSoup(yugipedia_text, "html.parser")
# 
#     #print(yugipedia_soup.prettify())
#     
#     card_table = yugipedia_soup.find("table", {"class":"innertable"}).find("tbody")
#     #print(card_table)
# 
#     rows = card_table.find_all("tr")
#     #print(rows)
#     
#     for row in rows:
#         if row.find("th").find("a") == None:
#             continue
#             
#         info = row.find("th").find("a").text 
#         #print(info)
# 
#         if info=="Password":
#             #print(row)
#             password = row.find("td").find("a").text
#             return password
# 
# print(find_password("Red-Eyes Black Dragon"))

# card_database = []
# 
# for row in match_cards_rows:
#     match_card_data = row.find_all("td")
#     #print(match_card_data)
#     #print(match_card_data[0])
#     
#     card_link = match_card_data[0].find("a")
#     card_name = sanitize(card_link.text)
#     card_appearance = match_card_data[1].text
#     print(card_name, card_appearance)
#     card_password = find_password(card_name)
#     print(card_password, card_appearance, card_name)
#     
#     card_database.append([find_password(card_name), card_appearance, card_name])
# 
# #print(card_database)

# In[ ]:




