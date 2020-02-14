#!/usr/bin/python
# coding=utf-8 

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from model import cards, boards, emailhelper
from model.config import Config

if __name__ == "__main__":
    conf = Config()
    board_id = conf.board_id

    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    cardsObj = cards.Cards(lists, labels)

    acceptedCards = cardsObj.getCardsFromLists(['Needs work', 'Scheduling', 'Ready to go', 'Program Ready']) 
    for card in acceptedCards:
        cardData = cards.decodeCard(card)
        print (cardData['contact']['email'])
