#!/usr/bin/env python3

import json
import requests
from . import users, trello, config, auth
import re

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
