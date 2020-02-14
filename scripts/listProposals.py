#!/usr/bin/python
# coding=utf-8 

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import sys
from model import cards, boards, emailhelper
from bottle import template
from model.config import Config
import io
import json

if __name__ == "__main__":
    conf = Config()
    board_id = conf.board_id

    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    cardsObj = cards.Cards(lists, labels)

    #data = cardsObj.getCardsFromLabel(['Lightning talk'], board_id)
    data = cardsObj.getCardsFromLabels(['Presentation','Panel'], board_id)
    for card in data:
        if not card['closed'] and card['idList'] in (lists['Questions on acceptance'],lists['Needs work'], lists['Ready to go']):
            print (card['name'].encode("utf-8"))
    #print(json.dumps(data,indent=4))


