from flask import request
from flask_restplus import Resource, fields

from bigleague.lib.sports import GAMES
from bigleague.views import expand_relations, get_uuid_field
from bigleague.storage.games import get_game, put_game, get_games


def get_game_fields():
    return {
        'event_name': fields.String(
            required=True,
            max_length=256,
            description='The name of the event'),
        'sport': fields.String(
            required=True,
            max_length=64,
            enum=GAMES,
            description='The sport. ' + str(GAMES)),
        'home_team_id': get_uuid_field(description='The home team\'s ID.'),
        'away_team_id': get_uuid_field(description='The away team\'s ID.'),
    }


def init_app(app, api):
    game_model = api.model('GameModel', get_game_fields())

    @api.route('/v1/game')
    class GameCreate(Resource):
        @api.expect(game_model, validate=True)
        def post(self):
            """Create a game."""
            game = put_game(request.get_json())
            if game:
                return expand_relations(game), 200
            else:
                return {}, 404

    @api.route('/v1/game/<uuid:game_id>')  # noqa
    class GameRead(Resource):
        @api.doc(params={'timestamp': 'Recall the game information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, game_id):
            """Retrieve game info from its ID."""
            game = get_game(id=game_id,
                            timestamp=request.args.get('timestamp', None))
            if game:
                return expand_relations(game), 200
            else:
                return {}, 404

    @api.route('/v1/games/by-sport/<string:sport>')  # noqa
    class GameRead(Resource):
        @api.doc(params={'timestamp': 'Recall the game information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, sport):
            """Retrieve games by sport."""
            games = get_games(sport=sport,
                              timestamp=request.args.get('timestamp', None))
            if games:
                return expand_relations(games), 200
            else:
                return {}, 404

    @api.route('/v1/games')  # noqa
    class GameRead(Resource):
        @api.doc(params={'timestamp': 'Recall the game information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self):
            """Retrieve all games."""
            games = get_games(timestamp=request.args.get('timestamp', None))
            if games:
                return expand_relations(games), 200
            else:
                return {}, 404
