"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    wins = ndb.IntegerProperty(default=0)
    total_played = ndb.IntegerProperty(default=0)
    min_move = ndb.IntegerProperty(default=999)

    def to_form(self):
        return UserForm(name=self.name,
                        email=self.email,
                        wins=self.wins,
                        total_played=self.total_played,
                        min_move=self.min_move)

    def add_win(self, num_move):
        """Add a win"""
        self.wins += 1
        self.total_played += 1
        if num_move < self.min_move:
            self.min_move = num_move
        self.put()

    def add_loss(self):
        """Add a loss"""
        self.total_played += 1
        self.put()

class Game(ndb.Model):
    """Game object"""
    user = ndb.KeyProperty(required=True, kind='User')
    board = ndb.PickleProperty(required=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    won = ndb.BooleanProperty(required=True, default=False)
    num_move = ndb.IntegerProperty(required=True, default=0)
    history = ndb.PickleProperty(required=True)

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        game = Game(user=user,
                    game_over=False,
                    num_move=0,
                    history=[])
        board_1d = range(0, 16)
        random.shuffle(board_1d)
        board_2d = [board_1d[i*4 : i*4+4] for i in range(0, 4)]
        game.board = board_2d
        game.put()
        return game

    def to_form(self):
        """Returns a GameForm representation of the Game"""
        form = GameForm(user_name=self.user.get().name,
                        urlsafe_key=self.key.urlsafe(),
                        board=str(self.board),
                        game_over=self.game_over,
                        num_move=self.num_move,
                        won=self.won,
                        history=str(self.history))
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost (resign)."""
        self.game_over = True
        self.put()
        score = Score(user=self.user,
                      date=date.today(),
                      won=won)
        score.put()
        if won:
            self.user.get().add_win(self.num_move)

        else:
            self.user.get().add_loss()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         won=self.won,
                         date=str(self.date))

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    user_name = messages.StringField(2, required=True)
    game_over = messages.BooleanField(3, required=True)
    won = messages.BooleanField(4, required=True)
    num_move = messages.IntegerField(5, required=True)
    board = messages.StringField(6, required=True)
    history = messages.StringField(7, required=True)

class GameForms(messages.Message):
    """Container for multiple GameForm"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)

class MakeMoveForm(messages.Message):
    """Used to make a move in an existing game"""
    move = messages.IntegerField(1, required=True)

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)

class UserForm(messages.Message):
    """User Form"""
    name = messages.StringField(1, required=True)
    email = messages.StringField(2)
    wins = messages.IntegerField(3, required=True)
    total_played = messages.IntegerField(4, required=True)
    min_move = messages.IntegerField(5, required=True)

class UserForms(messages.Message):
    """Container for multiple User Forms"""
    items = messages.MessageField(UserForm, 1, repeated=True)