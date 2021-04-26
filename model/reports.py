#!/usr/bin/python

import json
from . import trello, boards
import io
import csv


def trackReport(cardsObj):
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(('Track', 'Title', 'Type', 'Contact Email', 'Abstract'))
    for list in cardsObj.lists:
        for card in cardsObj.getCardsFromList(list):
            cardData = cardsObj.decodeCard(card)
            writer.writerow((list, card['name'], getType(card['labels']),  cardData['contact']['email'], cardData['abstract'].replace("</p><p>", "\n\n").replace("<p>","").replace("</p>","")))
            #print(json.dumps(card,indent=4))
    
    #  title, format, description, track, email
    return output.getvalue()

def getType(labels):
    types = ""
    for label in labels:
        if label['name'] in ["Open block (1 to 1.5 hours)","Lightning talk","Presentation (20mins)","Regional Meeting (1 to 2 hours)"]:
            if types:
                types += ", {}".format(label['name'])
            else:
                types = label['name']
    return types
    
