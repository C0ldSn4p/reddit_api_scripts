#!/usr/bin/python3

import requests
from requests.auth import HTTPBasicAuth
import json 
import time


#####################
### Inputs & Conf ###
#####################

# local configuration with secret key, see secret_key_empty
# Will need modflair and flair access
from secret_keys import conf 

userFlairDataFilename = "out_flair_data.py" #.py with all user flair data
flairListJsonFilename = "out_flair_list.json" #.json with the list of flair available
outputFilename = "flair_stats.txt"

subredditName = "france"

urlBase = 'http://oauth.reddit.com/r/'+subredditName+'/api/flairlist.json?limit=1000'
urlFlairList = 'https://oauth.reddit.com/r/'+subredditName+'/api/user_flair.json'


########################
### helper functions ###
########################

userFlairData = {} # global dict with the user flair data

def setupFile():
    with open(userFlairDataFilename, 'w') as out_file:
        out_file.write('userFlairData = {\n')

def finalizeFile():
    with open(userFlairDataFilename, 'a') as out_file:
        out_file.write('}\n')

def processFlairResponseJSON(response_text):
    jsonData = json.loads(response_text)
    if 'users' not in jsonData:
        print("Error no users")
        return ''
    users = jsonData['users']
    with open(userFlairDataFilename, 'a') as out_file:
        for user in users:
            try:
                username = user['user']
                flair = user.get('flair_css_class','None')
                if not isinstance(flair, str):
                    flair = 'ERROR None'
                out_file.write('"'+username+'":"'+flair+'",\n')
                userFlairData[username] = flair
            except TypeError:
                print(user)
                quit()
    return jsonData.get('next', '')
    
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



###############
#### Main  ####
###############

# Get flair list
print("Download list of available flairs")
x = requests.get(urlFlairList, headers = headers)
flairListRaw = x.text
with open(flairListJsonFilename, 'w') as out_file:
    out_file.write(flairListRaw)

# Get user flair data
print("Fetch user flair data")
setupFile()
k=1

url = urlBase
x = requests.get(urlBase, headers = headers)
next = processFlairResponseJSON(x.text)
print(str(k)+" | "+urlBase+" | "+next)

while next != '':
    k+=1
    url = urlBase+'&after='+next
    x = requests.get(urlBase+'&after='+next, headers = headers)
    next = processFlairResponseJSON(x.text)
    print(str(k)+" | "+url+" | "+next)
    waitIfNeeded(x)

finalizeFile()

# Process flair data into readable format
print("Process data")

flairList = json.loads(flairListRaw)

reverseTable = {}
addedFlairs = []

for item in flairList:
   reverseTable[item["css_class"]] = 0

for user,flair in userFlairData.items():
    if flair not in reverseTable:
        addedFlairs.append(flair)
        print("Add flair: "+flair)
        reverseTable[flair] = 0
    reverseTable[flair] += 1

reverseTupleList = []

for k,v in reverseTable.items():
    reverseTupleList.append((k,v))
    
reverseTupleList.sort(key=lambda t: t[1])


with open(outputFilename, 'w') as out_file:
    out_file.write("Raw data:\n"+str(reverseTupleList)+"\n----------------\n")
    for flair,count in reverseTupleList:
        if flair in addedFlairs:
            out_file.write(flair+' : '+str(count)+' | NOT IN THE LIST OF CURRENTLY AVAILABLE FLAIRS\n')
        else:
            out_file.write(flair+' : '+str(count)+'\n')

