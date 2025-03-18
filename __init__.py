from flask import Flask
from config import Config
from flasgger import Swagger
from app.utils.dictionary import load_dictionary

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Загрузим ка словарь
    load_dictionary()

    Swagger(app, template_file='docs/openapi.yml')

    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app