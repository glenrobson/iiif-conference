#!/usr/bin/env python3
import sys
import json
import os
import bottle
from bottle import route, run, template,debug, get, static_file, post, get,request, redirect, response
from beaker.middleware import SessionMiddleware
from cork import Cork
from model import cards, boards, users 
from model.config import Config

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

users.createUserFile(board_id)
boardUsers = users.getUsers(board_id)

cardsObj  = cards.Cards(lists, labels)

@post('/review/<cardId>.html')
def saveReview(cardId):
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]

    back = request.forms.get('Back')
    if back:
        redirect('../index.html')
    decision = request.forms.get('decision')
    comment = request.forms.get('comments')
    flagged = (request.forms.get('flag') == 'Flagged')
    #print ('Flagged: {} form: {}'.format(flagged, request.forms.get('flag')))
    #print (request.forms)

    cardsObj.review(user, cardId, decisionMap[int(decision)], comment, flagged)

    redirect('../index.html')

@get('/review/<cardId>.html')
def review(cardId):
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]
    data = cardsObj.getCard(cardId, user)

    #print (json.dumps(data,indent=4))
    output = template('views/showCard.tpl', card=data, user=user, decisions=decisionMap, role=aaa.current_user.role)
    return output

@route('/admin.html')
def showAdmin():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')
    
    return template('views/admin/admin.tpl', role=aaa.current_user.role)
      
@route('/admin/assignment.html')
def showAssignment():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    data = cardsObj.getCardsByUser(board_id)

    return template('views/admin/cardsByUser.tpl', data= data, role=aaa.current_user.role, lists=idLists)
@post('/admin/assignCard')
def assignCard():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    data = request.json
    results = cardsObj.assignCard(data['user_id'], data['card_id'])
    response.content_type = 'application/json'
    return json.dumps(results)

@get('/admin/assignCards.html')
def assignCards():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    return template('views/admin/assignCards.tpl', role=aaa.current_user.role)

@route('/admin/cards.json')
def showCards():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    response.content_type = 'application/json'
    data = cardsObj.getCardsByUser(board_id)
    return json.dumps(data)

@route('/admin/users.json')
def showUsers():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    response.content_type = 'application/json'
    data = users.getUsers(board_id)
    return json.dumps(data)

@route('/admin/proposalTypes.html')
def showProposalsByType():
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]
    aaa.require(role='admin', fail_redirect='/index.html')      

    data = cardsObj.getCardsByType(board_id, types=cardsObj.presentationTypes, exclude=['Rejected', 'Inbox'])
    return template('views/admin/proposalTypes.tpl', data=data, user=user, role=aaa.current_user.role, lists=idLists, cardsObj=cardsObj)
    
@route('/index.html')
@route('/')
def showIndex():
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]
    data = cardsObj.getCardsForUserFromBoard(user, board_id)

    #print (json.dumps(data,indent=4))
    output = template('views/showSubmissions.tpl', cardsJson=data, user=user, role=aaa.current_user.role, lists=idLists)
    return output
    
@get("/favicon.ico")
def favicon():
    return static_file('img/favicon.ico', root="static")

@get("/static/<filepath:path>")
def files(filepath):
    return static_file(filepath, root="static")

@post('/login')
def login():
    """Authenticate users"""
    username = request.forms.get('username')
    password = request.forms.get('password')
    print ('User {} pass {}'.format(username, password))
    aaa.login(username, password, success_redirect='/', fail_redirect='/login.html')

@get('/login.html')
def login():
    return template('views/login_form.tpl')
    
@route('/logout')
def logout():
    aaa.logout(success_redirect='/login.html')    

if __name__ == "__main__":
    aaa = Cork('conf')
    #print (aaa._hash('glen.robson@gmail.com','pass'))

    app = bottle.app()
    session_opts = {
        'session.cookie_expires': True,
        'session.encrypt_key': 'please use a random key and keep it secret!',
        'session.httponly': True,
        'session.timeout': 3600 * 24,  # 1 day
        'session.type': 'cookie',
        'session.validate_key': True,
    }
    app = SessionMiddleware(app, session_opts)

    debug(True)
    run(app=app, host='0.0.0.0', port=9000)
