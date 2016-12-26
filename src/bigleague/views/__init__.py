from flask_restplus import fields

from bottleneck import StorageError
from werkzeug.exceptions import BadRequest

from bigleague.storage.teams import get_team_fields, TEAM_TABLE
from bigleague.storage.games import get_game_fields, GAME_TABLE
from bigleague.storage.cells import get_cell_fields, CELL_TABLE
from bigleague.storage.players import get_player_fields, PLAYER_TABLE


def get_uuid_field(**kwargs):
    """Create a simple UUID field."""
    required = kwargs.pop('required', True)
    return fields.String(
        min_length=36,
        max_length=36,
        required=required,
        **kwargs)


def get_error_model(api, area):
    return api.model('%s_error' % area, {
        'message': fields.String(required=True,
                                 description='An explanation of the error.'),
    })


def get_expanders():
    return {
        'team': {
            'table': TEAM_TABLE,
            'fields': ['id', 'name'],
        },
        'home_team': {
            'table': TEAM_TABLE,
            'fields': ['id', 'name'],
        },
        'away_team': {
            'table': TEAM_TABLE,
            'fields': ['id', 'name'],
        },
        'player': {
            'table': PLAYER_TABLE,
            'fields': ['id', 'handle'],
        },
        'game': {
            'table': GAME_TABLE,
            'fields': get_game_fields(),
        },
        'cell': {
            'table': CELL_TABLE,
            'fields': get_cell_fields(),
        },
    }


def auto_expand(f):
    def wrapped(*args, **kwargs):
        ret, code = f(*args, **kwargs)
        try:
            return expand_relations(
                ret,
                expanders=get_expanders()), code
        except StorageError:
            raise BadRequest('Failed expansion')

    return wrapped


def expand_relations(*args, **kwargs):
    from bottleneck import expand

    kwargs.setdefault('expanders', get_expanders())
    return expand(*args, **kwargs)
