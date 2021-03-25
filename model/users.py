#!/usr/bin/python

import json
if __name__ != "__main__":
    from . import trello
    from .config import Config
else:
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from model import trello
    from model.config import Config

import requests
import sys
from cork import Cork

def getUsers(boardId):
    url = 'https://api.trello.com/1/boards/{}/members'.format(boardId)
    usersJson = trello.get(url).json()
    users  = {}
    for trelloUser in usersJson:
        users[trelloUser['username']] = trelloUser

    return users

def getUsersById(boardId):
    url = 'https://api.trello.com/1/boards/{}/members{}'.format(boardId, trello.getSecurity())
    usersJson = requests.get(url).json()
    users  = {}
    for trelloUser in usersJson:
        users[trelloUser['id']] = trelloUser

    return users

def getRole(boardId, userId):
    url = 'https://api.trello.com/1/boards/{}/memberships'.format(boardId)
    permissions = trello.get(url).json()
    role = "unknown"
    for permission in permissions:
        if permission['idMember'] == userId:
            #print ("Permissions")
            #print(json.dumps(permission, indent=4))
            role = permission['memberType']
            break
    #print ('Returning {}'.format(role))        
    return role            

def getCurrentUser():
    url = 'https://api.trello.com/1/members/me'
    usersJson = trello.get(url).json()
    return usersJson

