#!/usr/bin/python3

import requests
from requests.auth import HTTPBasicAuth
import json 
import time


#####################
### Inputs & Conf ###
#####################

# local configuration with secret key, see secret_key_empty
# Will need history access
from secret_keys import conf 

timestamp_cutoff = 1546300800 # timestamp cutoff for old account, here 01/01/19

# list of users to test, contains a list users with username
from inputList import users
# users = ['C0ldSn4p', 'Antitout'] #example

# output file name, will overwrite
outputfile = "result.txt"


########################
### helper functions ###
########################

def getLatestTimestamp(response_text):
    try:
        jsonData = json.loads(response_text)
        if 'data' not in jsonData:
            return -1
        data = jsonData['data']
        most_recent = data['children'][0]
        timestamp = most_recent['data']['created_utc']
        return timestamp
    except:
        return -2


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

active = []
old = []
dead = []
bug = []

total_str = str(len(users))
i = 1

urlbase = 'https://oauth.reddit.com/user/'

for user in users:
    x = requests.get(urlbase+user, headers = headers)
    timestamp = getLatestTimestamp(x.text)
    outstring = str(i).rjust(len(total_str), '0')+"/"+total_str+": "+user+" | "
    if(timestamp == -2):
        bug.append(user)
        outstring+="BUG"
    if(timestamp == -1):
        dead.append(user)
        outstring+="DEAD"
    elif(timestamp < timestamp_cutoff):
        old.append(user)
        outstring+="OLD"
    else:
        active.append(user)
        outstring+="Active"
    print(outstring)
    i+=1
    waitIfNeeded(x) # prevent too many request

print("active:")        
print(active)
print("old:")        
print(old)
print("dead:")        
print(dead)
print("bug:")        
print(bug)

####################
## Output to file ##
####################

with open(outputfile, 'w') as out_file:
    out_file.write("active:\n")
    out_file.write(str(active)+"\n")
    out_file.write("old:\n")
    out_file.write(str(old)+"\n")
    out_file.write("dead:\n")
    out_file.write(str(dead)+"\n")
    out_file.write("bug:\n")
    out_file.write(str(bug)+"\n")
    out_file.write("active+bug for new list:\n")
    out_file.write(str(active+bug)+"\n")
    
    