from flask_restplus import Resource


def init_app(app, api):
    @api.route('/health')
    class HelloWorld(Resource):
        def get(self):
            return {}
