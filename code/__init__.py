from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

import os

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

photos = UploadSet('photos', IMAGES)
#videos = UploadSet('videos', extensions='mp4')
videos = UploadSet('photos', extensions='mp4')

def create_app():
    app = Flask(__name__, instance_path=os.getcwd()+'/database')

    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    
    app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

    UPLOAD_FOLDER = "./uploads"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    # Configure the upload folder for videos
    configure_uploads(app, (photos, videos))
    

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # create database
    with app.app_context():
        db.create_all()

    return app

