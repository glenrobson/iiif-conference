#!/usr/bin/python

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from model import cards, boards
from model.config import Config
import yaml
import sys

def removeIfPresent(key, listsList):
    if key in listsList:
        listsList.remove(key)

if __name__ == "__main__":
    conf = Config()
    board_id = conf.board_id

    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    cardsObj = cards.Cards(lists, labels)
    listsToProcess = lists.keys()

    removeIfPresent('Rejected', listsToProcess)
    removeIfPresent('Reject', listsToProcess)
    removeIfPresent('Weak Reject', listsToProcess)

    acceptedCards = cardsObj.getCardsFromLists(listsToProcess) 

    outputList = []
    for card in acceptedCards:
        cardData = cardsObj.decodeCard(card)
        # Remove private submission related data:
        cardData.pop('comments', None)
        cardData.pop('contact', None)
        outputList.append(cardData)

    with open(sys.argv[1], 'w') as outfile:
        yaml.safe_dump(outputList, outfile, default_flow_style=False)    




