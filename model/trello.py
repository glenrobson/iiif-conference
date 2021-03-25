#!/usr/bin/python

import os
from bottle import request
from requests_oauthlib import OAuth1Session


def getSecurity():
    """Assign security tokens to URL

    This should only be used when its not possible to use the OAuth credentials i.e.
    when you need access to trello before the user has logged in. This might be during the
    setup of the system.
    """
    if 'trello_key' not in os.environ or 'trello_token' not in os.environ:
        raise EnvironmentError("You need to add trello_key and trello_token as an enviroment variable")

    key = os.environ['trello_key']
    token = os.environ['trello_token']
    

    return '?key={}&token={}'.format(key,token)        

def isLoggedIn():
    if 'beaker.session' in request.environ:
        session = request.environ['beaker.session']
        if 'user' not in session:
            return True
    return False            

def get(url):
    return oauth().get(url)

def post(url, params=None):
    if params:
        return oauth().post(url, params=params)
    else:
        return oauth().post(url)

def delete(url):
    return oauth().delete(url)

def put(url, params=None):
    if params:
        return oauth().put(url, params=params)
    else:
        return oauth().put(url)

def oauth():
    if 'trello_key' not in os.environ or 'trello_token' not in os.environ:
        raise EnvironmentError("You need to add trello_key and trello_token as an enviroment variable")

    if 'beaker.session' in request.environ:
        session = request.environ['beaker.session']

        key = os.environ['trello_key']
        token = os.environ['trello_token']

        oauth = OAuth1Session(key,
                          client_secret=token,
                          resource_owner_key=session['oauth_token'],
                          resource_owner_secret=session['oauth_secret'])
        return oauth
    else:        
        raise EnvironmentError("No session found. Do you need to login?")

if __name__ == "__main__":
    print (getSecurity())
