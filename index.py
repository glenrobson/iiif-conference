#!/usr/bin/env python3
import sys
import json
import os
import bottle
from bottle import route, run, template,debug, get, static_file, post, get,request, redirect, response
from beaker.middleware import SessionMiddleware
from model import cards, boards, users, auth 
from model.config import Config
import requests
from requests_oauthlib import OAuth1Session

client_id = "8a8baa2376c78e1ef98bef023637faac"
client_secret = "8811b7eaf802c8372bda59d0c3d24b2928a936e26ced7f895a899cfc2d80201a"
authorization_base_url = 'https://trello.com/1/OAuthAuthorizeToken'
access_token_url = 'https://trello.com/1/OAuthGetAccessToken'

conf = Config()
board_id = conf.board_id

decisionMap = {
    3: 'Strong Accept',
    2: 'Accept',
    1: 'Weak Accept',
    0: 'Borderline Paper',
    -1: 'Weak Reject',
    -2: 'Reject',
    -3: 'Request re-assignement'
}

(lists, idLists) = boards.getLists(board_id)
labels = boards.getLabels(board_id)

cardsObj  = cards.Cards(lists, labels)

def getCardsObj():
    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    return cards.Cards(lists, labels)

@post('/review/<cardId>.html')
def saveReview(cardId):
    auth.require(fail_redirect='/login.html')
    user = auth.getUser()

    back = request.forms.get('Back')
    if back:
        redirect('../index.html')
    decision = request.forms.get('decision')
    comment = request.forms.get('comments')
    flagged = (request.forms.get('flag') == 'Flagged')
    print ('Flagged: {} form: {}'.format(flagged, request.forms.get('flag')))
    print (request.forms)

    cardsObj = getCardsObj()
    print ("Cards list {}".format(cardsObj.lists))
    cardsObj.review(user, cardId, decisionMap[int(decision)], comment, flagged)

    redirect('../index.html')

@get('/review/<cardId>.html')
def review(cardId):
    auth.require(fail_redirect='/login.html')
    user = auth.getUser()
    data = cardsObj.getCard(cardId, user)

    #print (json.dumps(data,indent=4))
    output = template('views/showCard.tpl', card=data, user=user, decisions=decisionMap, role=auth.getRole())
    return output

@route('/admin.html')
def showAdmin():
    auth.require(role='admin', fail_redirect='/login.html')
    
    return template('views/admin/admin.tpl', role=auth.getRole())
      
@route('/admin/assignment.html')
def showAssignment():
    auth.require(role='admin', fail_redirect='/login.html')

    data = cardsObj.getCardsByUser(board_id)

    return template('views/admin/cardsByUser.tpl', data=data, role=auth.getRole(), lists=idLists)

@post('/admin/assignCard')
def assignCard():
    auth.require(role='admin', fail_redirect='/login.html')

    data = request.json
    results = cardsObj.assignCard(data['user_id'], data['card_id'])
    response.content_type = 'application/json'
    return json.dumps(results)

@get('/admin/assignCards.html')
def assignCards():
    auth.require(role='admin', fail_redirect='/login.html')

    return template('views/admin/assignCards.tpl', role=auth.getRole())

@route('/admin/cards.json')
def showCards():
    auth.require(role='admin', fail_redirect='/login.html')

    response.content_type = 'application/json'
    data = cardsObj.getCardsByUser(board_id)
    return json.dumps(data)

@route('/admin/users.json')
def showUsers():
    auth.require(role='admin', fail_redirect='/login.html')

    response.content_type = 'application/json'
    data = users.getUsers(board_id)
    return json.dumps(data)

@route('/admin/proposalTypes.html')
def showProposalsByType():
    auth.require(role='admin', fail_redirect='/login.html')

    data = cardsObj.getCardsByType(board_id, types=cardsObj.presentationTypes, exclude=['Rejected', 'Inbox'])
    return template('views/admin/proposalTypes.tpl', data=data, user=auth.getUser(), role=auth.getRole(), lists=idLists, cardsObj=cardsObj)
    
@route('/admin/setupLabels.html')
def setupLabels():
    auth.require(role='admin', fail_redirect='/login.html')
    labelsDetails = boards.getLabelDetail(board_id)

    cardsObj.labels = boards.getLabels(board_id)
    
    return template('views/admin/setupLabels.tpl', data=labelsDetails, user=auth.getUser(), role=auth.getRole())

@post('/admin/add_label')    
def addLabel():
    auth.require(role='admin', fail_redirect='/login.html')
    name = request.forms.get('name')
    colour = request.forms.get('color')
    boards.addLabel(board_id, name, colour)

    redirect('/admin/setupLabels.html') 

@route('/admin/setupLists.html')
def setupLists():
    auth.require(role='admin', fail_redirect='/login.html')
    listDetails = boards.getListDetail(board_id)

    cardsObj.lists = boards.getLists(board_id)
    print (cardsObj.lists)
    
    return template('views/admin/setupLists.tpl', data=listDetails, decisionList=list(decisionMap.values()),user=auth.getUser(), role=auth.getRole())

@post('/admin/add_list')    
def addList():
    auth.require(role='admin', fail_redirect='/login.html')
    name = request.forms.get('name')
    boards.addList(board_id, name)

    redirect('/admin/setupLists.html') 



@route('/index.html')
@route('/')
def showIndex():
    auth.require(fail_redirect='/login.html')
    user = auth.getUser()
    data = cardsObj.getCardsForUserFromBoard(user['id'], board_id)
    (lists, idLists) = boards.getLists(board_id)

    output = template('views/showSubmissions.tpl', cardsJson=data, user=user, role=auth.getRole(), lists=idLists)
    return output
    
@get("/favicon.ico")
def favicon():
    return static_file('img/favicon.ico', root="static")

@get("/static/<filepath:path>")
def files(filepath):
    return static_file(filepath, root="static")

@get('/callback')
def callback():
    oauth = OAuth1Session(client_id, client_secret=client_secret)
    oauth_response = oauth.parse_authorization_response(request.url)
    verifier = oauth_response.get('oauth_verifier')
    session = request.environ['beaker.session']

    oauth = OAuth1Session(client_id,
                          client_secret=client_secret,
                          resource_owner_key=session['tmp_oauth_token'],
                          resource_owner_secret=session['tmp_oauth_secret'],
                          verifier=verifier)

    oauth_tokens = oauth.fetch_access_token(access_token_url)
    resource_owner_key = oauth_tokens.get('oauth_token')
    resource_owner_secret = oauth_tokens.get('oauth_token_secret')

    # replace tempoary keys with permanent
    session['oauth_token'] = resource_owner_key
    session['oauth_secret'] = resource_owner_secret

    oauth = OAuth1Session(client_id,
                          client_secret=client_secret,
                          resource_owner_key=resource_owner_key,
                          resource_owner_secret=resource_owner_secret)

    auth.storeCurrentUser(board_id)
    redirect('/') 

@get('/login')
def login():
    session = request.environ['beaker.session']
    if auth.isAuthriosed():
        redirect('/') 
    
    if auth.haveTokens():
        auth.storeCurrentUser(board_id)
        redirect('/') 
        
    """Authenticate users"""
    oauth = OAuth1Session(client_id, client_secret=client_secret, callback_uri='https://conference.iiif.io/callback')
    fetch_response = oauth.fetch_request_token('https://trello.com/1/OAuthGetRequestToken')
    session['tmp_oauth_token'] = fetch_response.get('oauth_token')
    session['tmp_oauth_secret'] = fetch_response.get('oauth_token_secret')

    authorization_url = "{}&scope=read,write&name=IIIF Conference System&expiration=30days".format(oauth.authorization_url(authorization_base_url))

    redirect(authorization_url)

@get('/login.html')
def login():
    return template('views/login_form.tpl')
    
@route('/logout')
def logout():
    session = request.environ['beaker.session']
    # Might want to just delete the user here to retain the keys 
    # so it doesn't ask you to authorise every time..
    session.pop('user',None)
    #session.delete()
    redirect('/login.html')    

if __name__ == "__main__":

    app = bottle.app()
    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': 'please use a random key and keep it secret!',
        'session.httponly': True,
        'session.timeout': 3600 * 24,  # 1 day
        'session.type': 'file',
        'session.validate_key': True,
        'session.auto': True,
        'session.data_dir': "_session"
    }
    app = SessionMiddleware(app, session_opts)

    debug(True)
    run(app=app, host='0.0.0.0', port=9000, use_reloader=True, threaded=True)
