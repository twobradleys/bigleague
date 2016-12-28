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

    @api.route('/v1/team')
    class TeamCreate(Resource):
        @api.expect(team_model, validate=True)
        def post(self):
            """Create a team."""
            team = request.get_json()
            return expand_relations(put_team(team)), 201

    @api.route('/v1/team/<uuid:team_id>')
    class TeamRead(Resource):
        def get(self, team_id):
            """Retrieve info about a team."""
            team = get_team(team_id)
            if team:
                return expand_relations(team), 200
            else:
                return {}, 404

    @api.route('/v1/teams/by-sport/<string:sport>')
    class TeamReadBySport(Resource):
        def get(self, sport):
            """Retrieve info about all teams in a sport."""
            teams = get_teams_by_sport(sport)
            return expand_relations(teams), 200
