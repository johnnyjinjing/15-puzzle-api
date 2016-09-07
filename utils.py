"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints

def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity

# Find the position of zero
def find_zero(board):
    for row in range(4):
        for col in range(4):
            if board[row][col] == 0:
                return (row, col)

# CHeck if the user won the game
def game_won(board):
    for row in range(3):
        for col in range(4):
            if board[row][col] != row * 4 + col + 1:
                return False
    for col in range(3):
        if board(3, col) != 13 + col:
            return False
    return True