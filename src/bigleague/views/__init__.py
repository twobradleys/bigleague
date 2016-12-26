from flask_restplus import fields

from bottleneck import StorageError
from werkzeug.exceptions import BadRequest

from bigleague.storage.teams import get_team_fields, TEAM_TABLE


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
            'fields': get_team_fields(),
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
