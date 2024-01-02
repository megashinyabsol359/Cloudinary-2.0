from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    face_encoding = db.Column(db.PickleType)
    face_image = db.Column(db.LargeBinary)
    
class Track(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100))
    time_login = db.Column(db.String(100))
    is_login = db.Column(db.Boolean, nullable=False, default=True)
    time_logout = db.Column(db.String(100))
    