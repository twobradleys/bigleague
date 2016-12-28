from flask import Flask
from flask_restplus import Api

import bigleague.views.health
import bigleague.views.teams
import bigleague.views.players
import bigleague.views.cells
import bigleague.views.games
import bigleague.views.offers


def create_app_singletons():
    app = Flask('bigleague')
    api = Api(app, title='bigleague',
              description="""We're playing Squares, big league!

              Note that many endpoints allow for the use of `timestamp`
              parameters in order to see what the game looked like at a prior
              point in time.""")

    bigleague.views.health.init_app(app, api)
    bigleague.views.teams.init_app(app, api)
    bigleague.views.players.init_app(app, api)
    bigleague.views.cells.init_app(app, api)
    bigleague.views.games.init_app(app, api)
    bigleague.views.offers.init_app(app, api)

    return app, api
