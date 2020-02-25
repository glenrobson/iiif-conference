#!/usr/bin/python

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from model import cards, boards
from model.config import Config
import yaml
import sys

if __name__ == "__main__":
    conf = Config()
    board_id = conf.board_id

    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    cardsObj = cards.Cards(lists, labels)
    # Acceptance process build draft program
    if 'Strong Accept' in lists:
        acceptedCards = cardsObj.getCardsFromLists(['Strong Accept', 'Accept', 'Weak Accept', 'Borderline Paper']) 
    # Acceptance email gone. Ongoing contact work to get to approval    
    elif 'Questions on acceptance':    
        acceptedCards = cardsObj.getCardsFromLists(['Questions on acceptance','Scheduling', 'Needs work', 'Ready to go','Program Ready']) 
    # Final state, cleaning up last stragglers     
    else:    
        acceptedCards = cardsObj.getCardsFromLists(['Scheduling', 'Needs work', 'Ready to go','Program Ready']) 

    outputList = []
    for card in acceptedCards:
        #cardData = cards.decodeCard(card)

        outputList.append(card)

    with open(sys.argv[1], 'w') as outfile:
        yaml.safe_dump(outputList, outfile, default_flow_style=False)    




