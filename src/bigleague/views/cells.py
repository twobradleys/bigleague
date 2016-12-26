from flask import request
from flask_restplus import Resource

from bigleague.views import expand_relations
from bigleague.storage.cells import get_cell, get_cells


def init_app(app, api):
    @api.route('/v1/cell/<uuid:cell_id>')
    class CellReadById(Resource):
        @api.doc(params={'timestamp': 'Recall the cell information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, cell_id):
            """Retrieve a cell in a game by its ID."""
            cell = get_cell(id=cell_id,
                            timestamp=request.args.get('timestamp', None))
            if cell:
                return expand_relations(cell), 200
            else:
                return {}, 404

    @api.route('/v1/cell/by-game/<uuid:game_id>/by-index/<int:home_index>/<int:away_index>')  # noqa
    class CellReadByGameIdByIndex(Resource):
        @api.doc(params={'timestamp': 'Recall the cell information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, game_id, home_index, away_index):
            """Retrieve a cell in a game by its pre-shuffled index."""
            cell = get_cell(game_id=game_id, home_index=home_index,
                            away_index=away_index,
                            timestamp=request.args.get('timestamp', None))
            if cell:
                return expand_relations(cell), 200
            else:
                return {}, 404

    @api.route('/v1/cell/by-game/<uuid:game_id>/by-digits/<int:home_digits>/<int:away_digits>')  # noqa
    class CellReadByGameIdDigits(Resource):
        @api.doc(params={'timestamp': 'Recall the cell information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, game_id, home_digits, away_digits):
            """Retrieve a cell in a game by its digits."""
            cell = get_cell(game_id=game_id, home_digits=home_digits,
                            away_digits=away_digits,
                            timestamp=request.args.get('timestamp', None))
            if cell:
                return expand_relations(cell), 200
            else:
                return {}, 404

    @api.route('/v1/cells/by-game/<uuid:game_id>')
    class CellReadByGame(Resource):
        @api.doc(params={'timestamp': 'Recall the cell information at a '
                         'particular timestamp (in epoch milliseconds).'})
        def get(self, game_id):
            """Return cells for a game at a particular point in time."""
            cell = get_cells(game_id=game_id,
                             timestamp=request.args.get('timestamp', None))
            if cell:
                return expand_relations(cell), 200
            else:
                return {}, 404
