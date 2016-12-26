from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items

PLAYER_TABLE = 'player'


def get_player_fields():
    """The list of fields in the DB."""
    return [
        'id',
        'handle',
        'auth_token',
        'timestamp',
    ]


def get_players():
    """Get all the players."""
    return get_latest_items(PLAYER_TABLE, ['id', 'handle'])


def get_player(**conditions):
    """Lookup a player from the database."""
    conditions = {
        k: v for k, v in conditions.items()
        if k in ('id', 'handle', 'auth_token')}
    return get_item(conditions, PLAYER_TABLE, get_player_fields())


def put_player(player):
    """Place a player item into the database."""
    player = player.copy()
    player.setdefault('id', str(uuid4()))
    player.setdefault('auth_token', str(uuid4()))
    player.pop('timestamp', None)

    try:
        return put_item(player, PLAYER_TABLE, get_player_fields())
    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))
