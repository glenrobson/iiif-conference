#!/usr/bin/python
import sys
import json
import os
import bottle
from bottle import route, run, template,debug, get, static_file, post, get,request, redirect
from beaker.middleware import SessionMiddleware
from cork import Cork
from model import cards, boards, users 

board_id = '5c4adffeb3561e33298068b6'

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

users.createUserFile()
boardUsers = users.getUsers(board_id)

cards  = cards.Cards(lists, labels)

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

    cards.review(user, cardId, decisionMap[int(decision)], comment, flagged)

    redirect('../index.html')

@get('/review/<cardId>.html')
def review(cardId):
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]
    data = cards.getCard(cardId, user)

    #print (json.dumps(data,indent=4))
    output = template('views/showCard.tpl', card=data, user=user, decisions=decisionMap, role=aaa.current_user.role)
    return output

@route('/admin.html')
def showAdmin():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')
    
    return template('views/admin.tpl', role=aaa.current_user.role)
      
@route('/admin/assignment.html')
def showAssignment():
    aaa.require(fail_redirect='/login.html')
    aaa.require(role='admin', fail_redirect='/index.html')      

    data = cards.getCardsByUser(board_id)

    return template('views/cardsByUser.tpl', data= data, role=aaa.current_user.role, lists=idLists)

@route('/index.html')
@route('/')
def showIndex():
    aaa.require(fail_redirect='/login.html')
    user = boardUsers[aaa.current_user.username]
    data = cards.getCardsForUserFromBoard(user, board_id)

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
