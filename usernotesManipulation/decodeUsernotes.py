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

inputFile = "usernotes_purged.json" # .json from https://www.reddit.com/r/SUBREDDIT/wiki/usernotes

blobOutputFile = "clearTextUsernotes.json" 
humanReadableFile = "translatedUsernotes.txt"
humanReadableCSV = "translatedUsernotes.csv"
userListFile = "userlist.txt" # list of all users to be able to run other scripts on them (e.g. test if account active)
oldPermabannedUserListFile = "userlist_oldPermabanned.txt" # list of all users to be able to run other scripts on them (e.g. test if account active)

permabannedFlags = [9, 16] # tag of permanent ban
timestampCutOff = 1577836800 # 01/01/2020

########################
### Helper Functions ###
########################

def convertLink(s):
    try:
        sp = s.split(',')
        if len(sp) == 2:
            return "https://redd.it/"+sp[1]
        else:
            return "https://reddit.com/comments/"+sp[1]+"//"+sp[2]
    except:
        return s
        

class User:
    def __init__(self, username):
        self.username = username
        self.notes = []
        self.rawNotes = []
    
    def addNote(self, note):
        self.rawNotes.append(note)
        cleanNote = {}
        cleanNote['warning'] = warnings[note['w']]
        cleanNote['date'] = datetime.utcfromtimestamp(note['t']).strftime('%Y-%m-%d %H:%M:%S')
        cleanNote['mod'] = mods[note['m']]
        cleanNote['note'] = note['n']
        cleanNote['link'] = convertLink(note['l'])
        self.notes.append(cleanNote)
    
    def __str__(self):
        s = self.username+" ( https://reddit.com/u/"+self.username+" ):"
        noteCount = len(self.notes)
        curNote = noteCount
        for note in self.notes:
            note_str = '''
    %s/%s %s (%s) by %s at %s: 
            %s'''
            s += note_str % (str(curNote).rjust(len(str(noteCount)), '0'), str(noteCount), note['warning'], note['date'], note['mod'], note['link'], note['note'])
            curNote -=1
        return s
    
    def toCSV(self):
        s = ""
        first = True
        curNote = len(self.notes)
        for note in self.notes:
            s += '"'+self.username+'";https://reddit.com/u/'+self.username+';'+str(curNote)+';'+(note['warning'] if note['warning'] else "null")+';'+note['date']+';'+note['link']+';"'+(note['note'].replace('"', "'").replace(";","") if note['note'] else "null")+'"\n'
            first = False
            curNote -=1
        return s
        
    def isOldPermaBanned(self):
        return (self.rawNotes[0]['w'] in permabannedFlags) and (self.rawNotes[0]['t'] < timestampCutOff)



###############
#### Main  ####
###############

# extract
with open(inputFile,'r') as input:
    rawJson = json.loads(input.read())
blob = rawJson['blob']

# decode
cleartext = (zlib.decompress(base64.b64decode(blob))).decode("utf-8")

with open(blobOutputFile,'w') as output:
    output.write(cleartext)

# translate to human readable and produce userList
mods = rawJson['constants']['users']
warnings = rawJson['constants']['warnings']
usernotes = json.loads(cleartext)
userList = []
humanReadableNotes = []
oldPermabannedUserList = []

for user in usernotes:
    userList.append(user)
    userObj = User(user)
    for note in usernotes[user]['ns']:
        userObj.addNote(note)
    humanReadableNotes.append(userObj)
    if userObj.isOldPermaBanned():
        oldPermabannedUserList.append(user)

with open(humanReadableFile,'w') as output:
    for user in humanReadableNotes:
        output.write(str(user)+"\n")
        
with open(humanReadableCSV,'w') as output:
    output.write("username;userlink;noteCount;warningType;date;link;note\n")
    for user in humanReadableNotes:
        output.write(user.toCSV())

with open(userListFile,'w') as output:        
    output.write(str(userList))
    
with open(oldPermabannedUserListFile,'w') as output:        
    output.write(str(oldPermabannedUserList))