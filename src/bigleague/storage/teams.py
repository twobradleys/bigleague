from uuid import uuid4

from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items

TEAM_TABLE = 'team'


def get_team_fields():
    """The list of fields in the DB."""
    return [
        'id',
        'name',
        'sport',
        'timestamp',
    ]


def get_teams_by_sport(sport):
    """Get all the teams for a sport."""
    return get_latest_items(TEAM_TABLE, get_team_fields(),
                            conditions={'sport': sport})


def get_team(team_id, timestamp=None):
    """Lookup a Tag from the database."""
    return get_item(team_id, TEAM_TABLE, get_team_fields(), timestamp=timestamp)


def put_team(team):
    """Place a team item into the database."""
    team = team.copy()
    team.setdefault('id', str(uuid4()))
    try:
        return put_item(team, TEAM_TABLE, get_team_fields())
    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))
