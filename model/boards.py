#!/usr/bin/python

import json
from . import trello
import requests
import sys
from cork import Cork

def getBoards():
    url = 'https://api.trello.com/1/members/me{}'.format(trello.getSecurity())
    userJson = requests.get(url).json()
    
    url = 'https://api.trello.com/1/members/{}/boards{}'.format(userJson['id'],trello.getSecurity())
    response = requests.get(url)

    boards = response.json()
    print ('Please select a board id and add it to the config from the following list:')
    for board in boards:
        print (" * {}: {}".format(board['id'], board['name']))

def getLists(boardId):
    if not boardId:
        getBoards()
        raise EnvironmentError("Please select a board.")

    url = 'https://api.trello.com/1/boards/{}/lists{}&cards=none&fields=name'.format(boardId, trello.getSecurity())
    listsJson = requests.get(url).json()
    nameList = {}
    idList = {}
    for trelloList in listsJson:
        nameList[trelloList['name']] = trelloList['id']
        idList[trelloList['id']] = trelloList['name']

    return (nameList, idList) # return lists both ways, one with name as key and one id as a key

def getListDetail(boardId):
    url = 'https://api.trello.com/1/boards/{}/lists?cards=none&fields=all'.format(boardId)
    response = trello.get(url)
    #print(json.dumps(response.json(),indent=4))
    return response.json()

def addList(boardId, name):
    url = "https://api.trello.com/1/boards/{}/lists?name={}&pos=bottom".format(boardId, name)

    response = trello.post(url)
    if not response.ok:
        print ("Failed to add list due to {}: {}".format(response.status_code, response.text))

    return response

def getLabels(boardId):
    url = "https://api.trello.com/1/boards/{}/labels{}".format(boardId, trello.getSecurity())
    querystring = {"fields":"all","limit":"0"}
    response = requests.request("GET", url, params=querystring)

    labels = {}
    for label in response.json():
        labels[label['name']] = label['id']
    
    return labels

def getLabelDetail(boardId):
    url = "https://api.trello.com/1/boards/{}/labels?fields=all".format(boardId)
    response = trello.get(url)
    print(json.dumps(response.json(),indent=4))
    return response.json()

def addLabel(boardId, name, colour):
    url = "https://api.trello.com/1/boards/{}/labels?name={}&color={}".format(boardId, name, colour)

    response = trello.post(url)
    if not response.ok:
        print ("Failed to add label due to {}: {}".format(response.status_code, response.text))
    return response

if __name__ == "__main__":
    ## create user json
    board_id = '5c4adffeb3561e33298068b6'
   
