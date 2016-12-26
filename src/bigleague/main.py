import os

import config
from raven.contrib.flask import Sentry

from bigleague.app import create_app_singletons


def main():
    """Serve traffic."""
    config.init('bigleague')

    app, api = create_app_singletons()
    sentry_dsn = config.get('sentry.dsn')

    if sentry_dsn:
        Sentry(app, dsn=sentry_dsn)

    app.run(
        debug=True if os.environ.get('DEBUG') else False,
        port=int(os.environ.get('PORT', 80)),
        host=os.environ.get('HOST', '0.0.0.0'))
