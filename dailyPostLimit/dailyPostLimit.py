#!/usr/bin/python3

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.
#
# @author C0ldSn4p

import requests
from requests.auth import HTTPBasicAuth
import json 
import time
from datetime import datetime


#####################
### Inputs & Conf ###
#####################

# local configuration with secret key, see secret_key_empty
# Will need history access
from secret_keys import conf 

subredditName = 'france'
timeWindows = 24*60*60 # 1 day in seconds
postLimit = 4

cutoff = 3*timeWindows # will explore 3 timeWindows of content

timecutoff = time.time() - cutoff
print("time now "+str(time.time())+" | cutoff "+str(timecutoff))

rawdatafile = "rawdata.json"

########################
### Helper Functions ###
########################

def setupFile():
    with open(rawdatafile, 'w') as out_file:
        out_file.write('[\n')
        
def finalizeFile():
    with open(rawdatafile, 'a') as out_file:
        out_file.write('\n]\n')

def processPostResponseJSON(response_text, postHistory):
    jsonData = json.loads(response_text)

    data = jsonData['data']
    stop = False
    next = data.get('after','')
    if next == None: # reddit API limit or end of sub reached
        next = ''
    
    for itemRaw in data['children']:
        item = itemRaw['data']
        time = int(item['created'])
        author = item['author']
        link = "https://www.reddit.com"+item['permalink']
        if time < timecutoff: # exit loop if timecutoff is reached
            stop = True
            break
        
        if author not in postHistory:
            postHistory[author] = []
        postHistory[author].append((time, link))
    
    stop = (stop or next == '')
    
    with open(rawdatafile, 'a') as out_file:
        out_file.write(response_text)
        if not stop:
            out_file.write(",\n")
    
    return next, stop

def waitIfNeeded(response):
    headers = response.headers
    ratelimitRemaining = float(headers["x-ratelimit-remaining"])
    ratelimitReset = float(headers["x-ratelimit-reset"])
    if ratelimitRemaining < 5:
        print("WARNING: ratelimit close, sleep for "+str(ratelimitReset)+"s")
        time.sleep(ratelimitReset)

####################
###### Set Up ######
####################

# Set user agent
headers = requests.utils.default_headers()
headers.update({'User-Agent': conf['user_agent']})

# Auth and get token
auth=HTTPBasicAuth(conf['auth_id'], conf['auth_secret'])
url = 'https://www.reddit.com/api/v1/access_token'
data = {'grant_type': 'refresh_token', 'refresh_token': conf['refresh_token']}
x = requests.post(url, data = data, auth = auth, headers = headers)
response = json.loads(x.text)
access_token = response['access_token']

# update header
headers.update({'Authorization': 'bearer '+access_token})
print("token refreshed: "+x.text)


###################
#### Main loop ####
###################

urlBase = 'http://oauth.reddit.com/r/'+subredditName+'/new?limit=100'

postHistory = {}
setupFile()

k=0
url = urlBase
x = requests.get(urlBase, headers = headers)
next, stop = processPostResponseJSON(x.text, postHistory)
print(str(k)+" | "+urlBase+" | "+next)

while not stop:
    k+=1
    url = urlBase+'&after='+next
    x = requests.get(urlBase+'&after='+next, headers = headers)
    next, stop = processPostResponseJSON(x.text, postHistory)
    print(str(k)+" | "+url+" | "+next)
    if next == '':
        print('Cannot fetch more data through the API')
        print('Note that reddit history API seems to cap at 1000 posts')
    waitIfNeeded(x)

finalizeFile()

print("==========================================")
print("==========================================")
print("==========================================")
for author, history in postHistory.items():
    if len(history) > postLimit:
        flag = -1
        for i in range(len(history)-(postLimit+1)):
            if history[i][0]-history[i+postLimit+1][0] < timeWindows:
                flag = i
                break
        if flag >= 0:
            print(author+" (https://www.reddit.com/user/"+author+")")
            timestamp, link = history[flag]
            limit = timestamp - timeWindows
            i = 0
            while timestamp > limit:
                print("\t"+str(i+1)+" - "+datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S (UTC)')+" ("+str(timestamp)+"): "+link)
                i += 1
                timestamp, link = history[flag+i]
            print("------------------------------------------")

