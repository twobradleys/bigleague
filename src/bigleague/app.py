from flask import Flask
from flask_restplus import Api

import bigleague.views.health
import bigleague.views.teams
import bigleague.views.players


def create_app_singletons():
    app = Flask('bigleague')
    api = Api(app, title='bigleague',
              description="""We're playing Squares, big league!""")

    bigleague.views.teams.init_app(app, api)
    bigleague.views.players.init_app(app, api)
    bigleague.views.health.init_app(app, api)

    return app, api
