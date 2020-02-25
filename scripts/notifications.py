#!/usr/bin/python
# coding=utf-8 

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import sys
from model import cards, boards, emailhelper
from bottle import template
import io
import json
from model.config import Config

test=True

if __name__ == "__main__":
    type = sys.argv[1]
    conf = Config()
    board_id = conf.board_id

    (lists, idLists) = boards.getLists(board_id)
    labels = boards.getLabels(board_id)

    cardsObj = cards.Cards(lists, labels)

    if type == 'draft_program':
        acceptedCards = cardsObj.getCardsFromLists(['Ready to go']) 
        # for each submission
        for card in acceptedCards:
            cardData = cards.decodeCard(card)
            #print (json.dumps(cardData, indent=4))
            if 'type' in cardData and cardData['type'] != 'Workshop': # and cardData['id'] in [-1,0]:
                print ('Processing: Card: {}, type: {}'.format(cardData['id'], cardData['type']))
                # Create email card data
                emailData = {
                    'name': cardData['contact']['name'],
                    'title':cardData['title'],
                    'type': cardData['type'],
                    'url':'https://iiif.io/event/2019/goettingen/program/{}/'.format(cardData['id'])
                }
                emailClient = emailhelper.createEmailClient()

                fromAddr = 'glen.robson@iiif.io'
                # get contact email address
                if test:
                    to = 'glen.robson@gmail.com'
                else:
                    to = cardData['contact']['email']

                subject = '2019 IIIF Conference - draft program & registration'

                # create populated email template
                text = template('email_templates/program_released.txt', paper=emailData)

                if cardData['flagged']:
                    filename = "/tmp/flagged/{}.txt".format(cardData['id'])
                    print ('Saved email to {} in {} as presentation is flagged - {}'.format(cardData['contact']['email'], filename, card['name']))
                    with io.open(filename, mode="w", encoding='utf-8') as text_file:
                        text_file.write(u'To: {}\n'.format(to))
                        text_file.write(u'Subject: {}\n\n'.format(subject))
                        text_file.write(text)
                        text_file.close()
                else:
                    logo = emailhelper.createAttachment('static/img/logo_67_67.png', 'png')
                    message = emailhelper.createMessage(text=text, html=None, attachments = [logo])

                    # send email
                    print ('Emailing - {} regarding {}'.format(to, cardData['title']))
                    problems = emailClient.send(fromAddr, to, subject, message)

                    # add comment to card with email
                    comment = 'Contact\nType: Draft Program\nTo: {}\nEmail:\n\n'.format(to)
                    comment += text
                    cardsObj.addComment(card['id'], comment)

                    if problems:
                        print (problems)
                        comment = 'Contact\nType:problem\nDetails:\n'
                        comment += problems
                        cardsObj.updateFlagged(True)
                        cardsObj.addComment(card['id'], comment)
                    else:    
                        # move card to 'Ready to Go'
                        cardsObj.moveCardToList(card['id'], 'Program Ready')

    if type == 'accept_submission':
        # Get all submissions which are Strong Accept, Accept, Weak Accept, Borderline Paper
        acceptedCards = cardsObj.getCardsFromLists(['Strong Accept', 'Accept', 'Weak Accept', 'Borderline Paper']) 

        # for each submission
        for card in acceptedCards:
            cardData = cards.decodeCard(card)
            if 'type' in cardData:
                # Create email card data
                emailData = {
                    'name': cardData['contact']['name'],
                    'title':cardData['title'],
                    'type': cardData['type'],
                    'url': config.website('submission_url')['preview'].format(cardData['id'])
                }

                emailClient = emailhelper.createEmailClient()

                fromAddr = 'glen.robson@iiif.io'
                # get contact email address
                if test:
                    to = 'glen.robson@gmail.com'
                else:
                    to = cardData['contact']['email']

                subject = conf.email_template_config('accept_submission')['subject']

                # create populated email template
                text = template(conf.email_template_config('accept_submission')['text'], paper=emailData)

                if cardData['flagged']:
                    filename = "/tmp/flagged/{}.txt".format(cardData['id'])
                    print ('Saved email to {} in {} as presentation is flagged - {}'.format(cardData['contact']['email'], filename, card['name']))
                    with io.open(filename, mode="w", encoding='utf-8') as text_file:
                        text_file.write(u'To: {}\n'.format(to))
                        text_file.write(u'Subject: 2019 Göttingen IIIF Conference submission\n\n')
                        text_file.write(text)
                        text_file.close()
                else:
                    logo = emailhelper.createAttachment('static/img/logo_67_67.png', 'png')
                    message = emailhelper.createMessage(text=text, html=None, attachments = [logo])

                    # send email
                    print ('Emailing - {} regarding {}'.format(to, cardData['title']))
                    problems = emailClient.send(fromAddr, to, subject, message)

                    # add comment to card with email
                    comment = 'Contact\nType: acceptance\nTo: {}\nEmail:\n\n'.format(to)
                    comment += text
                    cardsObj.addComment(card['id'], comment)

                    if problems:
                        print (problems)
                        comment = 'Contact\nType:problem\nDetails:\n'
                        comment += problems
                        cardsObj.updateFlagged(True)
                        cardsObj.addComment(card['id'], comment)
                    else:    
                        if not test:
                            # move card to 'Ready to Go'
                            cardsObj.moveCardToList(card['id'], 'Ready to go')
            else:
                print ('Skipping as no type: {}'.format(card['name']))
            
