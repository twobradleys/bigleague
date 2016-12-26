from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items

CELL_TABLE = 'cell'


def get_cell_fields():
    """The list of fields in the DB."""
    return [
        'game_id',
        'home_index',
        'away_index',
        'timestamp',
        'home_digit',
        'away_digit',
        'player_id',
    ]


def get_cells(timestamp=None, **conditions):
    """Get all the cells."""
    return get_latest_items(CELL_TABLE, get_cell_fields(), timestamp=timestamp,
                            conditions=conditions)


def get_cell(**conditions):
    """Lookup a cell from the database."""
    cell_fields = get_cell_fields()
    conditions = {k: v for k, v in conditions.items()
                  if k in cell_fields}
    timestamp = conditions.pop('timestamp', None)
    return get_item(conditions, CELL_TABLE, get_cell_fields(),
                    timestamp=timestamp)


def put_cell(cell):
    """Place a cell into the database.

    There's a little fragility here because there's no hard enforcement that
    we're not changing the home and away digits from prior values.
    """
    cell = cell.copy()
    cell.pop('timestamp', None)

    try:
        return put_item(cell, CELL_TABLE, get_cell_fields(),
                        primary_keys=['game_id', 'home_index', 'away_index'])
    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))
