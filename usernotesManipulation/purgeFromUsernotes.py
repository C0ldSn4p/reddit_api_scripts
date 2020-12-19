#!/usr/bin/python3

# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# http://www.wtfpl.net/ for more details.
#
# @author C0ldSn4p

import json
import zlib
import base64
from datetime import datetime

#####################
### Inputs & Conf ###
#####################

inputFile = "usernotes.json" # .json from https://www.reddit.com/r/SUBREDDIT/wiki/usernotes
from users import usersToPurge # .py file containing the arrays listing the users to purge from the usernote DB

outputFile = "usernotes_purged.json"


###############
#### Main  ####
###############

# extract
with open(inputFile,'r') as input:
    rawJson = json.loads(input.read())
blob = rawJson['blob']
cleartext = (zlib.decompress(base64.b64decode(blob)))
notes = json.loads(cleartext)

print("purging "+str(len(usersToPurge))+" users")

notecount = 0
for user in usersToPurge:
    notecount += len(notes[user]['ns'])
    del notes[user]
    
print("purged "+str(notecount)+" usernotes")
    
newBlob = base64.b64encode(zlib.compress((json.dumps(notes,separators=(',', ':'))).encode('utf_8')))
rawJson['blob'] = newBlob.decode('utf_8')

with open(outputFile,'w') as output:        
    output.write(json.dumps(rawJson,separators=(',', ':')))
