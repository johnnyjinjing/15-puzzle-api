"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""


import logging
import endpoints
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, MakeMoveForm, ScoreForms, GameForms, UserForm, UserForms
from utils import get_by_urlsafe, find_zero, game_won

USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1, required=True),
    email=messages.StringField(2))
NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1))
MAKE_MOVE_REQUEST = endpoints.ResourceContainer(MakeMoveForm, urlsafe_game_key=messages.StringField(1))


@endpoints.api(name='the_fifteen_puzzle', version='v1')
class Fifteen_Puzzle_API(remote.Service):
    """Game API"""

    # Create a user
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException('A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(request.user_name))

    # Create a new game
    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')
        game = Game.new_game(user.key)
        return game.to_form()

    # Return current state of the game
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form()
        else:
            raise endpoints.NotFoundException('Game not found!')

    # Cancel game
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='POST')
    def cancel_game(self, request):
        """Cancel a game. Game must not have ended"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game and not game.game_over:
            game.end_game()
            game.put()
            return game.to_form()
        elif game and game.game_over:
            raise endpoints.BadRequestException('Game is already over!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    # Make a move
    @endpoints.method(request_message=MAKE_MOVE_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_move',
                      http_method='PUT')
    def make_move(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        if game.game_over:
            raise endpoints.NotFoundException('Game already over')

        move = request.move
        board = game.board
        # Find the location of zero
        zero_row, zero_col = find_zero(board)

        # Handling illegal move: 0 up, 1 down, 2 left, 3 right
        if move < 0 or move > 3:
            raise endpoints.BadRequestException('Invalid move: unknown direction!')
        if (move == 0 and zero_row == 3) or (move == 1 and zero_row == 0) or (move == 2 and zero_col == 3) or (move == 3 and zero_col == 0):
            raise endpoints.BadRequestException('Invalid move: out of bound!')

        # Move the tile
        if move == 0:
            board[zero_row][zero_col] = board[zero_row + 1][zero_col]
            board[zero_row + 1][zero_col] = 0
        elif move == 1:
            board[zero_row][zero_col] = board[zero_row - 1][zero_col]
            board[zero_row - 1][zero_col] = 0
        elif move == 2:
            board[zero_row][zero_col] = board[zero_row][zero_col + 1]
            board[zero_row][zero_col + 1] = 0
        elif move == 3:
            board[zero_row][zero_col] = board[zero_row][zero_col - 1]
            board[zero_row][zero_col - 1] = 0

        game.num_move += 1
        game.history.append(move)

        # Check if won after the move
        if game_won(board):
            game.end_game(user.key)

        game.put()
        return game.to_form()

    # Get game history
    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}/history',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Return a Game's move history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException('Game not found')
        return StringMessage(message=str(game.history))

    # Get all active games of a user
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='user/games',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Return all User's active games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.BadRequestException('User not found!')
        games = Game.query(Game.user == user.key).filter(Game.game_over == False)
        return GameForms(items=[game.to_form() for game in games])

    # Get score for all users
    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(items=[score.to_form() for score in Score.query()])

    # Get score for a paticular user
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException('A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    # Get the player has most game played
    @endpoints.method(response_message=UserForms,
                      path='highestscores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return all Users ranked by game played"""
        users = User.query().fetch()
        users = sorted(users, key=lambda x: x.wins, reverse=True)
        users = users[0:20]
        return UserForms(items=[user.to_form() for user in users])

    # Get the ranking sorted by the minimum move
    @endpoints.method(response_message=UserForms,
                      path='ranking',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return all Users ranked by minimum move"""
        users = User.query().fetch()
        users = sorted(users, key=lambda x: x.min_move)
        users = users[0:20]
        return UserForms(items=[user.to_form() for user in users])

api = endpoints.api_server([Fifteen_Puzzle_API])