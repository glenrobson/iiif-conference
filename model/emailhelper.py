#!/usr/bin/python

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import base64

from bottle import template

class EmailClient:
    smtpserver = ''
    username = ''
    password = ''
    from_addr = ''

    def __init__(self, smtpserver, username, password):
        self.smtpserver = smtpserver
        self.username = username
        self.password = password

    def send(self, from_addr, to, subject, message):
        #print (message.as_string())
        message["From"] = from_addr
        message["To"] = to
        message["Subject"] = subject
        #print (message.as_string())

       # print ('starting connection to: {}'.format(self.smtpserver))
        server = smtplib.SMTP_SSL(self.smtpserver)
        #server.set_debuglevel(True)
        #print ('logging in')
        response = server.login(self.username, self.password)
        #print (response)
        #print ('sending email')
        includeBcc = [to]
        if to != 'glen.robson@gmail.com':
            includeBcc.append('glen@iiif.io')
        problems = server.sendmail(from_addr, includeBcc, message.as_string())
        #print ('closing')
        server.quit()
        return problems

class GmailClient:

    def __init__(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.send'])
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('gmail', 'v1', credentials=creds)

    def send(self, from_addr, to, subject, message):
        message["From"] = from_addr
        message["To"] = to
        message["Subject"] = subject
        #print (message["From"])

        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        body = {'raw': raw}
        response = self.service.users().messages().send(userId="me", body=body).execute()
        #print ("Response")
        #print (response)
        
        # Need to figure out how to send an error
        return None

def createEmailClient(gmail=False):
    if gmail:
        return GmailClient()
    else:
        if 'SMTP' not in os.environ or 'SMTP_USER' not in os.environ or 'SMTP_PASS' not in os.environ:
            raise EnvironmentError("You need to add SMTP, SMTP_USER adn SMTP_PASS to your enviroment")

        smtpserver = os.environ['SMTP']
        username = os.environ['SMTP_USER']
        password = os.environ['SMTP_PASS']

        return EmailClient(smtpserver, username, password)

def createMessage(text=None,html=None,attachments=[]):
    if html is None:
        if attachments:
            message = MIMEMultipart()
            part1 = MIMEText(text.encode('utf-8'), "plain", 'utf-8')
            message.attach(part1)
        else:
            message = MIMEText(text.encode('utf-8'), "plain", 'utf-8')
    elif html and text:    
        message = MIMEMultipart()
        inner = MIMEMultipart("alternative")

        part1 = MIMEText(text.encode('utf-8'), "plain", 'utf-8')
        part2 = MIMEText(html, "html")        

        inner.attach(part1)
        inner.attach(part2)
        message.attach(inner)

    for attachment in attachments:
        message.attach(attachment)

    #print (message)
    return message

def createAttachment(filename, subtype, name=None):
    """
    subtype is the content after the slash in the mimetype e.g. png for image/png
    """
    if not name:
        name = filename
    with open(filename, 'rb') as file:
        attachment = MIMEImage(file.read(), _subtype=subtype)
        file.close()
        attachment.add_header('Content-Disposition', 'attachment', filename=name)
        return attachment

if __name__ == "__main__":
    emailClient = createEmailClient()

    fromAddr = 'glen.robson@iiif.io'
    to = 'glen.robson@gmail.com'
    subject = 'Test Message'
    content = 'This is a test message\n with a new line.. \nFancy!'
   

    paper = {
        'name':'Glen Robson',
        'title':'0. Test card by Glen Robson',
        'type': 'Lightning talk',
        'url':'https://preview.iiif.io/root/gottigen-program/event/2019/goettingen/program/0/'

    }
    text= template('email_templates/accept.txt', paper=paper)

    print (text)

    html="""\
        <html>
            <body><p>Test html <b>bold</b></p>
            </body>
            </html>
            """
    logo = createAttachment('static/img/logo_67_67.png', 'png')
    #with open('email_templates/signature-html.txt') as file:
    message = createMessage(text=text, html=None, attachments = [logo])
    problems = emailClient.send(fromAddr, to, subject, message)
    print (problems)


 
