#!/usr/bin/python

import os
import json

class Config:
    def __init__(self):
        if 'submission_config' not in os.environ:
            raise EnvironmentError("You need to add submission_config as an enviroment variable and point it to the config")
        
        with open(os.environ['submission_config']) as json_file:
            self.config = json.load(json_file)
    
    @property
    def board_id(self):
        return self.config['board_id']

    def email_template(self, name):    
        with open(self.config['email_templates'][name], 'r') as outfile:
            return outfile.read()

    def email_template_config(self, name):
        return self.config['email_templates'][name]

    def website(self, name):
        return self.config['website'][name]

if __name__ == "__main__":
    conf = Config()
    print (conf.board_id)
