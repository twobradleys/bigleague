from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import BadRequest

from bottleneck import put_item, get_item, get_latest_items

OFFER_TABLE = 'offer'
OFFER_OPEN = 'open'
OFFER_CLOSED = 'closed'
OFFER_STATES = [OFFER_OPEN, OFFER_CLOSED]
OFFER_TYPES = ['buy', 'sell']


def get_offer_fields():
    """The list of fields in the DB."""
    return [
        'game_id',
        'home_index',
        'away_index',
        'player_id',
        'timestamp',
        'type',
        'price',
        'counterparty_player_id',
        'timestamp_filled',
        'counterparty_price',
        'state',
    ]


def get_offers(timestamp=None, **conditions):
    """Get all the offers."""
    subfilters = list(
        set(['game_id', 'home_index', 'away_index', 'player_id']) -
        set(conditions.keys()))

    return get_latest_items(OFFER_TABLE, get_offer_fields(),
                            timestamp=timestamp, conditions=conditions,
                            subfilters=subfilters)


def get_offer(**conditions):
    """Lookup an offer from the database."""
    offer_fields = get_offer_fields()
    conditions = {k: v for k, v in conditions.items()
                  if k in offer_fields}
    timestamp = conditions.pop('timestamp', None)
    return get_item(conditions, OFFER_TABLE, get_offer_fields(),
                    timestamp=timestamp)


def put_offer(offer):
    """Place an offer into the database."""
    offer = offer.copy()
    offer.setdefault('state', OFFER_OPEN)
    offer.pop('timestamp', None)

    try:
        return put_item(
            offer, OFFER_TABLE, get_offer_fields(),
            primary_keys=['game_id', 'home_index', 'away_index', 'player_id'],
            defaults=['timestamp_filled', 'counterparty_player_id',
                      'counterparty_price', 'timestamp'])

    except IntegrityError as e:
        raise BadRequest('Integrity error %s in request. Please try again.' %
                         str(e))
