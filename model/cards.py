#!/usr/bin/env python3

import json
import requests
from . import users, trello, config, auth
import re

"""
    User Obj:

{
    "id": "6081a5a67c56bd0c0fe5c268",
    "checkItemStates": null,
    "closed": false,
    "dateLastActivity": "2021-04-22T18:40:37.396Z",
    "desc": "**Contact**\n - Sean Fraga, sfraga@usc.edu\n\n**Authors**\n- Sean Fraga, University of Southern California, United States\n- Christy Ye, University of Southern California, United States\n- Samir Ghosh, University of Southern California, United States\n\n**Comments**\n\n\n**Topics**\n- Interoperability in IIIF contexts and beyond\n- Discovering IIIF resources\n\n**Keywords:** Augmented reality, IIIF, \n\n**Abstract:**\n\tExisting viewers for IIIF-compliant materials, like Mirador and OpenSeadragon, make it possible for a user to interact with digitized resources across different repositories. But the web-based nature of these viewers means that these interactions are necessarily constrained by the size of the user\u2019s screen. This limits the amount of content in view, creates friction that impedes discovery, and divorces an item\u2019s content from its physical form. \n\tAugmented reality (AR) offers a new interface for user interaction with digitized archival materials, one that enables a user to interact with a digitized resource as if it were physically present in their real-world environment. Booksnake is an AR viewer for IIIF-compliant resources, presented as an iOS app. Booksnake connects IIIF\u2019s image and presentation APIs with Apple\u2019s ARKit, the AR technology built in to every recent iPhone and iPad. \n\tWith Booksnake, a user can select an IIIF-compliant resource, open their device\u2019s camera view, and overlay the digitized item on a horizontal surface in the real world. Booksnake anchors the digitized item to that surface and maintains the item\u2019s relative size and position. This enables the user to explore the item by physically moving around it, drawing closer to focus on key elements and stepping back to get the whole view, as if they were interacting with it in a reading room. \n\tBy using AR to recreate the embodied exploration of archival material in digitized form, Booksnake opens new possibilities for humanities computing, mixed reality, and teaching and learning. By leveraging an interface uniquely suited to mobile devices, Booksnake enriches interactions with IIIF resources and enables new discoveries.\n\tBooksnake is being developed by a multidisciplinary team of historians, librarians, artists, and computer programmers. The app is currently in beta testing. This presentation will discuss the project\u2019s genesis, explain how Booksnake uses IIIF APIs, showcase Booksnake\u2019s current capabilities, and preview future directions.\n",
    "descData": null,
    "dueReminder": null,
    "idBoard": "6081a5a67c56bd0c0fe5c1cd",
    "idList": "6081c2f8301bc53092c44aa3",
    "idMembersVoted": [],
    "idShort": 65,
    "idAttachmentCover": null,
    "idLabels": [
        "6081a5a67c56bd0c0fe5c298",
        "6081a5e769211287c61bff0e"
    ],
    "manualCoverAttachment": false,
    "name": "65. Introducing Booksnake: An Augmented Reality Viewer for IIIF-compliant Materials by Sean Fraga, Christy Ye and Samir Ghosh",
    "pos": 933889,
    "shortLink": "0Hho2Zx5",
    "isTemplate": false,
    "cardRole": null,
    "badges": {
        "attachmentsByType": {
            "trello": {
                "board": 0,
                "card": 0
            }
        },
        "location": false,
        "votes": 0,
        "viewingMemberVoted": false,
        "subscribed": false,
        "fogbugz": "",
        "checkItems": 0,
        "checkItemsChecked": 0,
        "checkItemsEarliestDue": null,
        "comments": 0,
        "attachments": 1,
        "description": true,
        "due": null,
        "dueComplete": false,
        "start": null
    },
    "dueComplete": false,
    "due": null,
    "idChecklists": [],
    "idMembers": [],
    "labels": [
        {
            "id": "6081a5a67c56bd0c0fe5c298",
            "idBoard": "6081a5a67c56bd0c0fe5c1cd",
            "name": "Presentation (20mins)",
            "color": "blue"
        },
        {
            "id": "6081a5e769211287c61bff0e",
            "idBoard": "6081a5a67c56bd0c0fe5c1cd",
            "name": "Accepted",
            "color": "lime"
        }
    ],
    "shortUrl": "https://trello.com/c/0Hho2Zx5",
    "start": null,
    "subscribed": false,
    "url": "https://trello.com/c/0Hho2Zx5/65-65-introducing-booksnake-an-augmented-reality-viewer-for-iiif-compliant-materials-by-sean-fraga-christy-ye-and-samir-ghosh",
    "cover": {
        "idAttachment": null,
        "color": null,
        "idUploadedBackground": null,
        "size": "normal",
        "brightness": "dark",
        "idPlugin": null
    }
}

"""

class Cards:
    security = ''
    # Hash table { 'listName' => 'list_id' }
    lists = {}
    # Hash table { 'label' => 'label_id' }
    labels = {}
    presentationTypes = ['Workshop', 'Lightning talk', 'Panel', 'Presentation']

    def __init__(self, lists, labels):
        self.security = trello.getSecurity()
        self.lists = lists
        self.labels = labels 
        conf = config.Config()
        self.board_id = conf.board_id

    def getCardsForUserFromBoard(self, user, boardId):
        url = 'https://api.trello.com/1/boards/{}/cards'.format(boardId)
        response = trello.get(url)
        response.raise_for_status()
        cards = response.json()
        userCards = []
        for card in cards:
            if user in card['idMembers']:
                userCards.append(card)
                
        return userCards        

    def getCardsFromLists(self, lists):
        allCards = []
        for listName in lists:
            listCards = self.getCardsFromList(listName)
            allCards += listCards

        return allCards    
            
    def getCardsFromList(self, listName):
        url = 'https://api.trello.com/1/lists/{}/cards{}'.format(self.lists[listName], self.security)
        return requests.get(url).json()

    def getCardsFromLabel(self, label, boardId):
        url = 'https://api.trello.com/1/search{}'.format(self.security)

        query = 'label:"{}" '.format(label)

        querystring = {
            "query":query,
            "idBoards":boardId,
            "card_fields":"all",
            "cards_limit":"100",
            "cards_page":"0"
        }
        return requests.request("GET", url, params=querystring).json()['cards']

    def getCardsFromLabels(self, labels, boardId):
        cards = []
        for label in labels:
            cards += self.getCardsFromLabel(label,boardId)
        return cards        

   # def getCardsFromLists(self, lists):
   #     cards = []
   #     for trelloList in lists:
   #         url = 'https://api.trello.com/1/lists/{}/cards{}'.format(self.lists[trelloList.encode('utf-8')], self.security)
   #         listCards = requests.get(url).json()
   #         cards.extend(listCards)
   #             
   #     return cards            

    def getCard(self, cardId, user=None):
        url = 'https://api.trello.com/1/cards/{}'.format(cardId)
        # add reviews
        card = trello.get(url).json()
        if user:
            reviews = self.getReviews(cardId, user)
            if reviews:
                card['review'] = reviews[0]
        return card    

    def review(self, user, cardId, decision, comment, flagged):
        # add Flag
        self.updateFlagged(cardId, flagged)

        # add or update comment
        previousReview = self.getReviews(cardId, user)
        if decision == 'Request re-assignement':
            # add comment
            url = "https://api.trello.com/1/cards/{}/actions/comments".format(cardId)
            querystring = {"text":"{} requested resasignment.\nComment:\n{}".format(user['fullName'], comment)}
            response = trello.post(url, params=querystring)
            # remove membership
            url = "https://api.trello.com/1/cards/{}/idMembers/{}".format(cardId, user['id'])
            response = trello.delete(url)

            # move card to inbox
            url = "https://api.trello.com/1/cards/{}?idList={}".format(cardId, self.lists['Inbox'])
            response = trello.put(url)
        else:
            text = encodeReview(user, decision, comment)
            if previousReview: # this is an update
                url = "https://api.trello.com/1/cards/{}/actions/{}/comments".format(cardId, previousReview[0]['id'])
                querystring = {"text": text}
                response = trello.put(url, params=querystring)
            else: # This is new
                url = "https://api.trello.com/1/cards/{}/actions/comments".format(cardId)
                querystring = {"text":text}
                response = trello.post(url, params=querystring)
                #print ('{}: {}'.format(response.status_code, response.text))

            if decision not in self.lists:
                print ('Failed to find "{}" in:'.format(decision))
                print (self.lists)
            else:    
                # move card to correct list if not already there
                url = "https://api.trello.com/1/cards/{}?idList={}".format(cardId, self.lists[decision])
                response = trello.put(url)

    def addComment(self, cardId, comment):
        url = "https://api.trello.com/1/cards/{}/actions/comments".format(cardId)
        querystring = {"text":comment}
        response = trello.put(url, params=querystring)
        
    def addList(self, listName):
        if listName not in self.lists:
            url = "https://api.trello.com/1/lists{}&name={}&idBoard={}&pos=bottom".format(self.security, listName, self.board_id)
            response = requests.request("POST", url).json()
            # {"id":"5e55aecef6e56b8dff840794","name":"test list","closed":false,"idBoard":"5e45bec960c5af7dbe375164","pos":475135,"limits":{}}
            self.lists[response['name']] = response['id']
            return response['id']
        else:
            return self.lists[listName]

    def moveCardToList(self, cardId, listName):
        if listName not in self.lists:
            list_id = self.addList(listName)
        else:
            list_id = self.lists[listName]
            
        url = "https://api.trello.com/1/cards/{}{}&idList={}".format(cardId, self.security, list_id)
        response = requests.request("PUT", url)

    def assignCard(self, userId, cardId):
        # First remove all other assigned users
        url = 'https://api.trello.com/1//cards/{}/members'.format(cardId)
        members = trello.get(url).json()
        for member in members:
            url = 'https://api.trello.com/1/cards/{}/idMembers/{}'.format(cardId, member['id'])
            response = trello.delete(url)

        if userId:
            # Then add new one
            url = 'https://api.trello.com/1/cards/{}/idMembers?value={}'.format(cardId, userId)

            response = trello.post(url)
            if response.status_code == 200:
                return { "status": "Success"}
            else:
                return { 
                    "status":"error",
                    "description": response.reason
                }
        else:
            # If user is none then is should be unassigend i.e. no user assigned
            return { "status": "Success"}

    def updateFlagged(self, cardId, flagged):
        card = self.getCard(cardId)
        cardFlagged = False
        for label in card['labels']:
            if label['name'] == 'Flagged':
                cardFlagged = True
                break

        if flagged and not cardFlagged:
            # add flagged label
            url = "https://api.trello.com/1/cards/{}/idLabels?value={}".format(cardId, self.labels['Flagged'])
            self.printResponse(trello.post(url))

        if cardFlagged and not flagged:
            # remove flagged label
            url = "https://api.trello.com/1/cards/{}/idLabels/{}".format(cardId, self.labels['Flagged'])
            self.printResponse(trello.delete(url))
            
    def getCardsByUser(self, boardId):
        # Get all Cards
        url = 'https://api.trello.com/1/boards/{}/cards'.format(boardId)
        cards = trello.get(url).json()
        boardUsers = users.getUsersById(boardId)
        userCards = {}
        userCards['Unassigned'] = []
        for card in cards:
            if card['idMembers']:
                for idMember in card['idMembers']:
                    if not boardUsers[idMember]['fullName'] in userCards:
                        userCards[boardUsers[idMember]['fullName']] = []
                    userCards[boardUsers[idMember]['fullName']].append(card)    
            else:
                userCards['Unassigned'].append(card)
                
        return userCards

    def getCardsByType(self, board_id, types=None, include=None, exclude=None):    
        lists = self.lists
        if include:
            lists = include

        if exclude:    
            lists = lists.copy()
            for value in exclude:
                if value in lists:
                    del lists[value]

        if not types:
            types = self.labels

        results = {} 
        for listName in lists:
            for card in self.getCardsFromList(listName):
                for label in card['labels']:
                    if label['name'] in types:
                        if label['name'] not in results:
                            results[label['name']] = []
                        results[label['name']].append(card)

        return results            
        

    def printResponse(self, response):
        if response.status_code != 200:
            print (response.text)

    def getReviews(self, cardId, user=None):    
        url = 'https://api.trello.com/1/cards/{}/actions'.format(cardId)

        reviews = []
        for comment in trello.get(url).json():
            if 'text' in comment['data'] and comment['data']['text'].startswith('Review:'):
                if user: # if user is supplied only return the ones linked to the correct user
                    if user['id'] in comment['idMemberCreator']:
                        reviews.append(comment)
                else: # if no user return all valid reviews
                    reviews.append(comment)
        return reviews        

    def decodeCard(self, card):
        cardData = {
            'id': int(re.findall(r"^[0-9]+", card['name'])[0]),
            'title': re.sub(r"^[0-9]+. (.*) by .*$", r"\1", card['name'])
        }
        cardData['flagged'] = False
        for label in card['labels']:
            if label['name'] == 'Flagged':
                cardData['flagged'] = True
            else:
                if label['name'] in self.presentationTypes:
                    cardData['type'] = label['name']
        mode = ""        
        for line in card['desc'].splitlines():
            if line == '**Contact**':
                mode = 'Contact'
            elif line == '**Authors**':
                mode = 'Author'
            elif line == '**Comments**':
                mode = 'Comment'
            elif line == '**Topics**':
                mode = 'Topic'
            elif line.startswith('**Keywords:**'):
                cardData['keywords'] = []
                for keyword in line[14:].split(','):
                    cardData['keywords'].append(keyword.strip())

            elif line == '**Abstract:**':
                mode = 'Abstract'
            else:
                #print ('mode {} line "{}" '.format(mode, line))
                if mode == 'Contact' and line.startswith(' - '):
                    cardData['contact'] = {
                        'name': line[3:].split(',')[0],
                        'email': line.split(', ')[1]
                    }
                elif mode == 'Author' and line.startswith('- '):    
                    if 'authors' not in cardData:
                        cardData['authors'] = []
                    authorText = line[2:] 
                    link = ''
                    if authorText.startswith('['):
                        # this is a link in the form [name, company, location](url)
                        link = re.sub(r'^\[.*\]\((.*)\)',r'\1', authorText)
                        authorText = re.sub(r'^\[(.*)\]\(.*$',r'\1', authorText)
                    author = {
                        'name': authorText.split(',')[0],
                        'company': authorText.split(', ')[1],
                    }
                    if len(line.split(', ')) > 2:
                        author['location'] = authorText.split(', ')[2]
                    if link:
                        author['link'] = link
                    cardData['authors'].append(author)
                elif mode == 'Comment' and len(line.strip()) > 0:
                    if 'comments' not in cardData:
                        cardData['comments'] = line
                    else:
                        cardData['comments'] += line

                elif mode == 'Topic' and line.startswith('- '):    
                    if 'topics' not in cardData:
                        cardData['topics'] = [ line[2:] ]
                    else:
                        cardData['topics'].append(line[2:])

                elif mode == 'Abstract':
                    if 'abstract' not in cardData:
                        cardData['abstract'] = line + '\n'
                    else:
                        cardData['abstract'] += line + '\n'
                        
        cardData['abstract'] = '<p>{}</p>'.format(cardData['abstract'].replace("\n\n","</p><p>"))
        return cardData

def encodeReview(user, decision, comment):
    return 'Review:\nReviewer: {}\nDecision: {}\nComment:{}'.format(user['fullName'],decision, comment) 

def decodeReview(text):
    lines = text.split('\n')

    comment = lines[3].split(':')[1].strip() + '\n'
    if len(lines) > 4:
        for line in lines[4:]:
            comment += line + '\n'

    return (lines[1].split(':')[1].strip(), lines[2].split(':')[1].strip(), comment)



if __name__ == "__main__":
    cards = Cards({
        'Inbox': '5c4ae07b7a5fd74927f127a2'
    }, {})
    print (json.dumps(cards.getCardsForUserFromList('59881f6d2d479882cef5ce9c', '5c4ae07b7a5fd74927f127a2'), indent=4)) # my user id
