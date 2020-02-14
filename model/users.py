#!/usr/bin/python

import json
import trello
import requests
import sys
from config import Config
from cork import Cork

def getUsers(boardId):
    url = 'https://api.trello.com/1/boards/{}/members{}'.format(boardId, trello.getSecurity())
    usersJson = requests.get(url).json()
    users  = {}
    for trelloUser in usersJson:
        users[trelloUser['username'].encode('ascii','replace')] = trelloUser

    return users

def getUsersById(boardId):
    url = 'https://api.trello.com/1/boards/{}/members{}'.format(boardId, trello.getSecurity())
    usersJson = requests.get(url).json()
    users  = {}
    for trelloUser in usersJson:
        users[trelloUser['id'].encode('ascii','replace')] = trelloUser

    return users

def createUserFile(board_id):
    ## create user json
    users = getUsers(board_id)
    users_json = {}
    # need to ensure there is a file there before we create aaa
    with open('./conf/users.json', 'w') as outfile:
        json.dump(users_json, outfile)
    aaa = Cork('conf')
    for user in users.values():
        role = 'user'
        if user['username'] in ['glenrobson2','joshhadro2']:
            role = 'admin'
        user_json = {
            'hash': aaa._hash(user['username'], user['fullName'].split(' ')[0]),
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
