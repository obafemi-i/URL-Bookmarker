from flask import Flask, jsonify, redirect
from src.auth.auth import auth
from src.bookmarks.bookmarks import bookmarks
from src.database.database import db, Bookmark
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from src.config.swagger import template, swagger_config
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
import os

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.environ.get('SQLALCHEMY_DB_URI'),
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET'),

            # swagger config
            SWAGGER={
                'title': 'Bookmarks API',
                'uiversion': 3
            }
        )
    
    else:
        app.config.from_mapping(test_config)


    
    db.app = app
    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)

    # api for increasing vists' count for each short url
    @app.get('/<short_url>')
    @swag_from('./docs/short_url.yml')
    def redirect_short_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()

            return redirect(bookmark.url)  # redirect to the actual url mapped to the short url


    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Page not found'}), HTTP_404_NOT_FOUND
    
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, please try agian'}), HTTP_500_INTERNAL_SERVER_ERROR
    
    return app

