#!/usr/bin/python

import json
import trello
import requests
import users
import re

class Cards:
    security = ''
    lists = {}
    labels = {}
    def __init__(self, lists, labels):
        self.security = trello.getSecurity()
        self.lists = lists
        self.labels = labels 

    def getCardsForUserFromBoard(self, user, boardId):
        url = 'https://api.trello.com/1/boards/{}/cards{}'.format(boardId, self.security)
        cards = requests.get(url).json()

        userCards = []
        for card in cards:
            if user['id'] in card['idMembers']:
                userCards.append(card)
                
        return userCards        

    def getCardsFromLists(self, lists):
        cards = []
        for trelloList in lists:
            url = 'https://api.trello.com/1/lists/{}/cards{}'.format(self.lists[trelloList], self.security)
            listCards = requests.get(url).json()
            cards.extend(listCards)
                
        return cards            

    def getCard(self, cardId, user=None):
        url = 'https://api.trello.com/1/cards/{}{}'.format(cardId, self.security)
        # add reviews
        card = requests.get(url).json()
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
            url = "https://api.trello.com/1/cards/{}/actions/comments{}".format(cardId, self.security)
            querystring = {"text":"{} requested resasignment.\nComment:\n{}".format(user['fullName'], comment)}
            response = requests.request("POST", url, params=querystring)
            # remove membership
            url = "https://api.trello.com/1/cards/{}/idMembers/{}{}".format(cardId, user['id'], self.security)
            response = requests.request("DELETE", url)

            # move card to inbox
            url = "https://api.trello.com/1/cards/{}{}&idList={}".format(cardId, self.security, self.lists['Inbox'])
            response = requests.request("PUT", url)
        else:
            text = encodeReview(user, decision, comment)
            if previousReview: # this is an update
                print ('Updating comment')
                url = "https://api.trello.com/1/cards/{}/actions/{}/comments{}".format(cardId, previousReview[0]['id'], self.security)
                querystring = {"text": text}
                response = requests.request("PUT", url, params=querystring)
            else: # This is new
                print ('adding comment')
                url = "https://api.trello.com/1/cards/{}/actions/comments{}".format(cardId, self.security)
                querystring = {"text":text}
                response = requests.request("POST", url, params=querystring)

            print (self.lists)
            if decision not in self.lists:
                print ('Failed to find "{}" in:'.format(decision))
                print (self.lists)
            else:    
                # move card to correct list if not already there
                url = "https://api.trello.com/1/cards/{}{}&idList={}".format(cardId, self.security, self.lists[decision])
                response = requests.request("PUT", url)


    def assignCard(self, userId, cardId):
        # First remove all other assigned users
        url = 'https://api.trello.com/1//cards/{}/members{}'.format(cardId, self.security)
        members = requests.get(url).json()
        for member in members:
            url = 'https://api.trello.com/1/cards/{}/idMembers/{}{}'.format(cardId, member['id'], self.security)
            response = requests.request("DELETE", url)

        if userId:
            # Then add new one
            url = 'https://api.trello.com/1/cards/{}/idMembers{}&value={}'.format(cardId, self.security, userId)

            response = requests.request("POST", url)
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

        print ('User is {}, card is {}'.format(flagged, cardFlagged))
        if flagged and not cardFlagged:
            # add flagged label
            url = "https://api.trello.com/1/cards/{}/idLabels{}&value={}".format(cardId, self.security, self.labels['Flagged'])
            print ('Posting to {}'.format(url))
            self.printResponse(requests.request("POST", url))

        if cardFlagged and not flagged:
            # remove flagged label
            url = "https://api.trello.com/1/cards/{}/idLabels/{}{}".format(cardId, self.labels['Flagged'], self.security)
            self.printResponse(requests.request("DELETE", url))
            
    def getCardsByUser(self, boardId):
        # Get all Cards
        url = 'https://api.trello.com/1/boards/{}/cards{}'.format(boardId, self.security)
        cards = requests.get(url).json()
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

    def printResponse(self, response):
        if response.status_code != 200:
            print (response.text)

    def getReviews(self, cardId, user=None):    
        url = 'https://api.trello.com/1/cards/{}/actions{}'.format(cardId, self.security)

        reviews = []
        for comment in requests.get(url).json():
            if 'text' in comment['data'] and comment['data']['text'].startswith('Review:'):
                if user: # if user is supplied only return the ones linked to the correct user
                    if user['fullName'] in comment['data']['text']:
                        reviews.append(comment)
                else: # if no user return all valid reviews
                    reviews.append(comment)
        return reviews        

def encodeReview(user, decision, comment):
    return 'Review:\nReviewer: {}\nDecision: {}\nComment:{}'.format(user['fullName'],decision, comment) 

def decodeReview(text):
    lines = text.split('\n')

    comment = lines[3].split(':')[1].strip() + '\n'
    if len(lines) > 4:
        for line in lines[4:]:
            comment += line + '\n'

    return (lines[1].split(':')[1].strip(), lines[2].split(':')[1].strip(), comment)

def decodeCard(card):
    cardData = {
        'id': re.findall(r"^[0-9]+", card['name'])[0],
        'title': re.sub(r"^[0-9]+. (.*) by .*$", r"\1", card['name'])
    }
    cardData['flagged'] = False
    for label in card['labels']:
        if label['name'] == 'Flagged':
            cardData['flagged'] = True
        else:
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
                
                author = {
                    'name': line[2:].split(',')[0],
                    'company': line.split(', ')[1],
                }
                if len(line.split(', ')) > 2:
                    author['location'] = line.split(', ')[2]

                cardData['authors'].append(author)
            elif mode == 'Comment' and len(line.strip()) > 0:
                if 'comments' not in cardData:
                    cardData['comments'] = line
                else:
                    cardData['comments'] += line

            elif mode == 'Topic' and line.startswith('- '):    
                if 'topic' not in cardData:
                    cardData['topic'] = [ line[2:] ]
                else:
                    cardData['topic'].append(line[2:])

            elif mode == 'Abstract':
                if 'abstract' not in cardData:
                    cardData['abstract'] = line + '\n'
                else:
                    cardData['abstract'] += line + '\n'
                    
    cardData['abstract'] = '<p>{}</p>'.format(cardData['abstract'].encode('utf-8').replace("\n\n","</p><p>"))
    return cardData

if __name__ == "__main__":
    cards = Cards({
        'Inbox': '5c4ae07b7a5fd74927f127a2'
    }, {})
    print (json.dumps(cards.getCardsForUserFromList('59881f6d2d479882cef5ce9c', '5c4ae07b7a5fd74927f127a2'), indent=4)) # my user id
