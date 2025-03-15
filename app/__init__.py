from flask import Flask
from config import Config
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    Swagger(app, template_file='docs/openapi.yml')

    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app