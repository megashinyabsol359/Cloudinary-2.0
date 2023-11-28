from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, IMAGES, configure_uploads

# from flask_socketio import SocketIO, emit
# import io
# from io import StringIO
# import cv2
# from PIL import Image
# import base64
# import imutils
# import numpy as np

# from flask_talisman import Talisman




# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # ###
    
    # Talisman(app)
    
    # socketio = SocketIO(app)
    
    # @socketio.on('image')
    # def image(data_image):
    #     sbuf = StringIO()
    #     sbuf.write(data_image)

    #     # decode and convert into image
    #     b = io.BytesIO(base64.b64decode(data_image))
    #     pimg = Image.open(b)

    #     ## converting RGB to BGR, as opencv standards
    #     frame = cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)

    #     # Process the image frame
    #     frame = imutils.resize(frame, width=700)
    #     frame = cv2.flip(frame, 1)
    #     imgencode = cv2.imencode('.jpg', frame)[1]

    #     # base64 encode
    #     stringData = base64.b64encode(imgencode).decode('utf-8')
    #     b64_src = 'data:image/jpg;base64,'
    #     stringData = b64_src + stringData

    #     # emit the frame back
    #     emit('response_back', stringData)
    # socketio.init_app(app)
    # ########


    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    
    app.config['UPLOADED_PHOTOS_DEST'] = 'uploads'

    photos = UploadSet('photos', IMAGES)
    configure_uploads(app, photos)

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

