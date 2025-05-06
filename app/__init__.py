from flask import Flask
from config import Config
from flasgger import Swagger
from app.utils.dictionary import load_dictionary

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = 'Буэээээээ'

    # Я хз как так получилось что словарь у нас глобальный и не объектный, но это надо исправляты. Когда-нибудь. Идёт в долг
    load_dictionary()

    # Захостим документацию
    Swagger(app, template_file='docs/openapi.yml')

    from app.routes import main_routes
    app.register_blueprint(main_routes)

    return app