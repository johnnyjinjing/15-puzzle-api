#!/usr/bin/env python

"""main.py - This file contains handlers that are called by taskqueue and/or
cronjobs."""
import logging

import webapp2
from google.appengine.api import mail, app_identity
from api import Fifteen_Puzzle_API
from utils import get_by_urlsafe
from models import User, Game


class SendReminderEmail(webapp2.RequestHandler):
    def get(self):
        """Send a reminder email to each User with an email who has
        games in progress. Email body includes a count of active games and their
        urlsafe keys
        Called every hour using a cron job"""
        users = User.query(User.email != None)

        for user in users:
            games = Game.query(Game.user == user.key).filter(Game.game_over == False)
            if games.count() > 0:
                subject = 'This is a reminder!'
                body = 'Hello {}, you have {} games in progress. Their' \
                       ' keys are: {}'.\
                    format(user.name,
                           games.count(),
                           ', '.join(game.key.urlsafe() for game in games))
                logging.debug(body)
                # This will send test emails, the arguments to send_mail are:
                # from, to, subject, body
                mail.send_mail('noreply@{}.appspotmail.com'.
                               format(app_identity.get_application_id()),
                               user.email,
                               subject,
                               body)

app = webapp2.WSGIApplication([
    ('/crons/send_reminder', SendReminderEmail),
], debug=True)
