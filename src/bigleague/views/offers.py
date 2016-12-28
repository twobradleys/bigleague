from flask import request
from flask_restplus import Resource, fields
from werkzeug.exceptions import BadRequest

from config.serialize import serialize
from bigleague.storage.offers import (get_offer, get_offers, OFFER_TYPES,
                                      OFFER_STATES, OFFER_CLOSED, put_offer)
from bigleague.storage.cells import get_cell
from bigleague.storage.players import get_player
from bigleague.views import get_uuid_field


def get_offer_fields():
    return {
        'price': fields.Integer(
            required=False,
            min=0,
            default=50,
            description='The amount of the offer. '),
        'type': fields.String(
            required=False,
            enum=OFFER_TYPES,
            default='buy',
            description='Whether you are buying or selling.'),
        'state': fields.String(
            required=False,
            enum=OFFER_STATES,
            default='open',
            description='Whether you are buying or selling.'),
        'player_id': get_uuid_field(
            description='The player placing the offer.'),
    }


def init_app(app, api):  # noqa
    offer_model = api.model('OfferModel', get_offer_fields())

    @api.route('/v1/offers/<uuid:game_id>')
    class GetOffers(Resource):
        @api.doc(params={
            'timestamp': ('Recall the offers available at a '
                          'particular timestamp (in epoch milliseconds) '
                          '(optional).'),
            'state': ('Whether you want to see open or closed '
                      'offers. Valid choices are ["open", "closed"] (optional).'),
            'player_id': 'Filter on a particular player (optional).',
            'home_index': 'The home team index (optional).',
            'away_index': 'The away team index (optional).',
        })
        def get(self, game_id):
            """Retrieve all offers in a game by the game ID."""
            state = request.args.get('state')
            home_index = request.args.get('home_index')
            away_index = request.args.get('away_index')

            conditions = {
                'timestamp': request.args.get('timestamp', None),
            }

            if 'player_id' in request.args:
                conditions['player_id'] = request.args['player_id']

            if state:
                if state not in OFFER_STATES:
                    raise BadRequest("Invalid state filter: %s" % state)
                else:
                    conditions['state'] = state

            if home_index:
                conditions['home_index'] = home_index

            if away_index:
                conditions['away_index'] = away_index

            offers = get_offers(game_id=game_id, **conditions)

            if offers:
                return serialize(offers), 200
            else:
                return {}, 404

        @api.expect(offer_model, validate=True)
        def put(self, game_id, home_index, away_index):
            """Put an offer to buy or sell a cell."""
            offer_request = request.get_json()
            player_id = offer_request.get('player_id')

            if offer_request['state'] == OFFER_CLOSED:
                return close_offer(player_id, game_id, home_index,
                                   away_index)

            else:
                price = offer_request.get('price')
                type = offer_request.get('type')
                if not price or not type:
                    raise BadRequest(
                        "In order to place or update an offer, you must supply "
                        "both 'price' and 'type'.")

                return place_offer(player_id, game_id, home_index, away_index,
                                   price, type)


def close_offer(player_id, game_id, home_index, away_index):
    """Handle closing of an offer."""
    if not player_id:
        raise BadRequest("'player_id' must be specified.")

    existing_offer = get_offer(game_id=game_id,
                               home_index=home_index,
                               away_index=away_index,
                               player_id=player_id)

    if not existing_offer:
        raise BadRequest("No existing offer found.")

    if existing_offer['state'] == OFFER_CLOSED:
        return {}, 200

    existing_offer['state'] = OFFER_CLOSED
    return serialize(put_offer(existing_offer)), 200


def place_offer(player_id, game_id, home_index, away_index, price, type_):
    """Place or update an offer on a cell."""
    cell = get_cell(game_id=game_id, home_index=home_index,
                    away_index=away_index)
    if not cell:
        raise BadRequest("Cell does not exist?")

    player = get_player(id=player_id)
    if not player:
        raise BadRequest("Invalid player_id: %s" % player_id)

    if type_ == 'sell':
        if cell['player_id'] != player_id:
            raise BadRequest("You cannot sell a cell you do not own.")

    elif type_ == 'buy':
        if cell['player_id'] == player_id:
            raise BadRequest("You cannot buy a cell you own.")

    offer = put_offer({
        'game_id': game_id,
        'home_index': home_index,
        'away_index': away_index,
        'player_id': player_id,
        'type': type_,
        'price': price,
    })
    return serialize(offer), 200
