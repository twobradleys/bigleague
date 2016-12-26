from flask import request
from flask_restplus import Resource, fields

from bigleague.views import expand_relations
from bigleague.storage.teams import get_team, put_team, get_teams_by_sport


def get_team_fields():
    return {
        'name': fields.String(
            required=True,
            max_length=256,
            description='The name of the team'),
        'sport': fields.String(
            required=True,
            max_length=256,
            description='The sport the team plays'),
    }


def init_app(app, api):
    team_model = api.model('Team', get_team_fields())

    @api.route('/team')
    class TeamCreate(Resource):
        @api.expect(team_model, validate=True)
        def post(self):
            team = request.get_json()
            return expand_relations(put_team(team)), 201

    @api.route('/team/<uuid:team_id>')
    class TeamRead(Resource):
        def get(self, team_id):
            team = get_team(team_id)
            if team:
                return expand_relations(team), 200
            else:
                return {}, 404

    @api.route('/teams/<string:sport>')
    class TeamReadBySport(Resource):
        def get(self, sport):
            team = get_teams_by_sport(sport)
            if team:
                return expand_relations(team), 200
            else:
                return {}, 404
