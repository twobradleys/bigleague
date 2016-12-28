from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items
from bigleague.storage.cells import get_cell, put_cell
from bigleague.storage.offers import put_offer
from bigleague.lib.sports import GameState
from bigleague.lib.house import HOUSE_PLAYER_ID

GAME_TABLE = 'game'


def get_game_fields():
    """The list of fields in the DB."""
    return [
        'id',
        'timestamp',
        'event_name',
        'sport',
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
    game.pop('timestamp', None)

    try:
        return put_item(game, GAME_TABLE, get_game_fields())
    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))


def ensure_cells_exist(game_id):
    game = get_game(id=game_id)
    if not game:
        raise BadRequest(
            "Game does not exist: %s" % game_id)

    for home_index in range(10):
        for away_index in range(10):
            cell = get_cell(game_id=game_id, home_index=home_index,
                            away_index=away_index)
            if cell:
                raise BadRequest(
                    """Cell (home_index=%d, away_index=%d) already exists in
                    game %s""" % (home_index, away_index, game_id))

            cell = put_cell({
                'game_id': game_id,
                'home_index': home_index,
                'away_index': away_index,
                'home_digit': None,
                'away_digit': None,
                'player_id': HOUSE_PLAYER_ID,
            })

            put_offer({
                'game_id': cell['game_id'],
                'home_index': cell['home_index'],
                'away_index': cell['away_index'],
                'player_id': HOUSE_PLAYER_ID,
                'type': 'sell',
                'price': 50,
            })
