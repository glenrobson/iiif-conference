#!/usr/bin/python

import os

def getSecurity():
    if 'trello_key' not in os.environ or 'trello_token' not in os.environ:
        raise EnvironmentError("You need to add trello_key and trello_token as an enviroment variable")

    key = os.environ['trello_key']
    token = os.environ['trello_token']

    return '?key={}&token={}'.format(key,token)        
 
if __name__ == "__main__":
    print (getSecurity())
