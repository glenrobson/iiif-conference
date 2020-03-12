#!/usr/bin/python

import json
from . import trello
import requests
import sys
from cork import Cork

def getLists(boardId):
    url = 'https://api.trello.com/1/boards/{}/lists{}&cards=none&fields=name'.format(boardId, trello.getSecurity())
    listsJson = requests.get(url).json()
    nameList = {}
    idList = {}
    for trelloList in listsJson:
        nameList[trelloList['name']] = trelloList['id']
        idList[trelloList['id']] = trelloList['name']

    return (nameList, idList) # return lists both ways, one with name as key and one id as a key

def getLabels(boardId):
    url = "https://api.trello.com/1/boards/{}/labels{}".format(boardId, trello.getSecurity())
    querystring = {"fields":"all","limit":"0"}
    response = requests.request("GET", url, params=querystring)

    labels = {}
    for label in response.json():
        labels[label['name']] = label['id']
    
    return labels


if __name__ == "__main__":
    ## create user json
    board_id = '5c4adffeb3561e33298068b6'
   
