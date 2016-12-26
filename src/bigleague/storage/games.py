import json
from uuid import uuid4

from config.serialize import serialize
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items
from bigleague.lib.sports import GameState

GAME_TABLE = 'game'


def get_game_fields():
    """The list of fields in the DB."""
    return [
        'id',
        'timestamp',
        'event_name',
        'sport',
        'history',
        'state',
        'home_team_id',
        'away_team_id',
        'home_score',
        'away_score',
    ]


def get_games(timestamp=None, **conditions):
    """Get all the games."""
    return get_latest_items(GAME_TABLE, get_game_fields(), timestamp=timestamp,
                            conditions=conditions)


def get_game(**conditions):
    """Lookup a game from the database."""
    game_fields = get_game_fields()
    conditions = {k: v for k, v in conditions.items()
                  if k in game_fields}
    timestamp = conditions.pop('timestamp', None)
    return get_item(conditions, GAME_TABLE, get_game_fields(),
                    timestamp=timestamp)


def put_game(game):
    """Place a game into the database."""
    game = game.copy()
    game.setdefault('id', str(uuid4()))
    game.setdefault('home_score', 0)
    game.setdefault('away_score', 0)
    game.setdefault('state', GameState.pregame)
    game.setdefault('history', [])
    game.pop('timestamp', None)

    try:
        game['history'] = json.dumps(serialize(game['history']))
        return put_item(game, GAME_TABLE, get_game_fields())
    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))
