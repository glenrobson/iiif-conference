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
    url = 'https://api.trello.com/1/boards/{}/members{}'.format(boardId, trello.getSecurity())
    usersJson = requests.get(url).json()
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

def createUserFile(board_id):
    ## create user json
    users = getUsers(board_id)
    users_json = {}
    # need to ensure there is a file there before we create aaa
    with open('./conf/users.json', 'w') as outfile:
        json.dump(users_json, outfile)
    aaa = Cork('conf')
    print ('Preferred algorithum {}'.format(aaa.preferred_hashing_algorithm))
    for user in users.values():
        role = 'user'
        if user['username'] in ['glenrobson2','joshhadro2']:
            role = 'admin'
        user_json = {
            'hash': aaa._hash(user['username'], user['fullName'].split(' ')[0]).decode("utf-8"),
            'desc': user['fullName'],
            'role': role,
            'email_addr': ''
        }    
        users_json[user['username']] = user_json

    with open('./conf/users.json', 'w') as outfile:
        json.dump(users_json, outfile)

if __name__ == "__main__":
    conf = Config()
    board_id = conf.board_id

    if len(sys.argv) > 1:
        email = conf.email_template('account_info')
        # Print emails
        users = getUsers(board_id)
        for user in users.values():
            username = user['username']
            password = user['fullName'].split(' ')[0]

            print(email.format(username, password))

    else:
        createUserFile(board_id)
