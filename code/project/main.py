from flask import Blueprint, render_template, send_from_directory, url_for, current_app
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from . import db
from . import opencv

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

photos = UploadSet('photos', IMAGES)

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    submit = SubmitField('Upload')

@main.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(current_app.config['UPLOADED_PHOTOS_DEST'], filename)

@main.route('/RGBtoGray', methods = ['GET', 'POST'])
@login_required
def RGBtoGray():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        gray_filename = opencv.RGBtoGray(filename, file_url)
        gray_file_url = url_for('main.get_file', filename=gray_filename)
    else:
        file_url = None
        gray_file_url = None
    return render_template('RGBtoGray.html', form = form, file_url = file_url, gray_file_url = gray_file_url)

@main.route('/face_detection', methods = ['GET', 'POST'])
@login_required
def face_detection():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = opencv.face_detection(filename, file_url)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    return render_template('face_detection.html', form = form, file_url = file_url, face_file_url = face_file_url)
