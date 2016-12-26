from flask import request
from flask_restplus import Resource, fields

from bigleague.views import expand_relations
from bigleague.storage.players import get_player, put_player, get_players


def get_player_fields():
    return {
        'handle': fields.String(
            required=True,
            max_length=256,
            description='The name of the player'),
    }


def init_app(app, api):
    player_model = api.model('Player', get_player_fields())

    @api.route('/v1/player')
    class PlayerCreate(Resource):
        @api.expect(player_model, validate=True)
        def post(self):
            """Create a player. HACK."""
            player = request.get_json()
            return expand_relations(put_player(player)), 201

    @api.route('/v1/player/by-<string:identifier>/<string:handle>')
    class PlayerRead(Resource):
        def get(self, identifier, handle):
            """Get player info by an identifier. (id or handle)."""
            player = get_player(**{identifier: handle})
            if player:
                return expand_relations(player), 200
            else:
                return {}, 404

    @api.route('/v1/players')
    class PlayersRead(Resource):
        def get(self):
            """Get all the players."""
            player = get_players()
            if player:
                return expand_relations(player), 200
            else:
                return {}, 404
