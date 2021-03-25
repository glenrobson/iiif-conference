#!/usr/bin/python

import json
if __name__ != "__main__":
    from . import trello
    from . import users
    from .config import Config
else:
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from model import trello, users
    from model.config import Config

from bottle import request,redirect

def storeCurrentUser(boardId):
    user = users.getCurrentUser()
    session = request.environ['beaker.session']
    session['user'] = user
    
    user['role'] = users.getRole(boardId, user['id'])

def require(fail_redirect=None, role=None):    
    if not isAuthriosed():
        redirect(fail_redirect)
    else:
        if role and role != getRole():
            redirect(fail_redirect)
    
def isAuthriosed():
    session = request.environ['beaker.session']
    return 'user' in session

def haveTokens():
    session = request.environ['beaker.session']
    return 'oauth_token' in session

def getUser():
    session = request.environ['beaker.session']
    return session['user']
    
def getRole():
    user = getUser()
    if 'role' in user:
        return getUser()['role']
    else:
        return 'unknown'
