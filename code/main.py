from flask import Blueprint, render_template, send_from_directory, url_for, current_app, request, Response, send_file, jsonify, flash
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from . import db
from . import imgedit
from . import videoedit
from . import photos, videos
from moviepy.editor import VideoFileClip

import numpy as np

from werkzeug.utils import secure_filename

import base64
import os

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

class ImageUploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(photos, 'Only images are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    submit = SubmitField('Upload')
    
class VideoUploadForm(FlaskForm):
    photo = FileField(
        validators=[
            FileAllowed(videos, 'Only images are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    submit = SubmitField('Upload')

class MultiVideoUploadForm(FlaskForm):
    video1 = FileField(
        validators=[
            FileAllowed(videos, 'Only mp4 videos are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    video2 = FileField(
        validators=[
            FileAllowed(videos, 'Only mp4 videos are allowed.'),
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
    form = ImageUploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        gray_filename = imgedit.RGBtoGray(filename, file_url)
        gray_file_url = url_for('main.get_file', filename=gray_filename)
    else:
        file_url = None
        gray_file_url = None
    return render_template('imgedit_RGBtoGray.html', form = form, file_url = file_url, gray_file_url = gray_file_url)

@main.route('/face_detection', methods = ['GET', 'POST'])
@login_required
def face_detection():
    form = ImageUploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = imgedit.face_detection(filename, file_url)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    return render_template('imgedit_face_detection.html', form = form, file_url = file_url, face_file_url = face_file_url)

@main.route('/crop', methods = ['GET', 'POST'])
@login_required
def crop():
    form = ImageUploadForm()
    if form.validate_on_submit():
        x1 = int(request.form.get('x1'))
        x2 = int(request.form.get('x2'))
        y1 = int(request.form.get('y1'))
        y2 = int(request.form.get('y2'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        crop_filename = imgedit.crop(filename, file_url, x1, x2, y1, y2)
        crop_file_url = url_for('main.get_file', filename=crop_filename)
    else:
        file_url = None
        crop_file_url = None
    print(file_url)
    return render_template('imgedit_crop.html', form = form, file_url = file_url, crop_file_url = crop_file_url)

@main.route('/rotate', methods = ['GET', 'POST'])
@login_required
def rotate():
    form = ImageUploadForm()
    if form.validate_on_submit():
        angle = int(request.form.get('degree'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        rotate_filename = imgedit.rotate(filename, file_url, angle)
        rotate_file_url = url_for('main.get_file', filename=rotate_filename)
    else:
        file_url = None
        rotate_file_url = None
    return render_template('imgedit_rotate.html', form = form, file_url = file_url, rotate_file_url = rotate_file_url)

@main.route('/resize', methods = ['GET', 'POST'])
@login_required
def resize():
    form = ImageUploadForm()
    if form.validate_on_submit():
        size = int(request.form.get('size'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        resize_filename = imgedit.resize(filename, file_url, size)
        resize_file_url = url_for('main.get_file', filename=resize_filename)
    else:
        file_url = None
        resize_file_url = None
    return render_template('imgedit_resize.html', form = form, file_url = file_url, resize_file_url = resize_file_url)

@main.route('/hsv', methods = ['GET', 'POST'])
@login_required
def hsv():
    form = ImageUploadForm()
    if form.validate_on_submit():
        h = int(request.form.get('hue'))
        s = int(request.form.get('saturation'))
        v = int(request.form.get('light'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        hsv_filename = imgedit.hsv(filename, file_url, h, s, v)
        hsv_file_url = url_for('main.get_file', filename=hsv_filename)
    else:
        file_url = None
        hsv_file_url = None
    return render_template('imgedit_hsv.html', form = form, file_url = file_url, hsv_file_url = hsv_file_url)

@main.route('/object_detection', methods = ['GET', 'POST'])
@login_required
def object_detection():
    video_url = None
    image_url = None
    object_file_url = None
    image_form = ImageUploadForm()
    video_form = VideoUploadForm()
    if video_form.validate_on_submit():
        filename = videos.save(video_form.photo.data)
        video_url = url_for('main.get_file', filename=filename)        
        # video = video_form.photo.data
        # video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(video.filename))
        # file_url = url_for('main.get_file', filename=video.filename)
        # video.save(video_path)
        object_filename = videoedit.object_detection(filename, video_url)
        object_file_url = url_for('main.get_file', filename=object_filename)
        # filename = photos.save(video_form.photo.data)
        # file_url = url_for('main.get_file', filename=filename)
        # gray_filename = imgedit.object_detection(filename, file_url)
        # gray_file_url = url_for('main.get_file', filename=gray_filename)
    elif image_form.validate_on_submit():
        filename = photos.save(image_form.photo.data)
        image_url = url_for('main.get_file', filename=filename)
        object_filename = imgedit.object_detection(filename, image_url)
        object_file_url = url_for('main.get_file', filename=object_filename)
        
    return render_template('imgedit_object_detection.html', form = image_form, image_url = image_url, video_url = video_url, object_file_url = object_file_url)

@main.route('/trim_video', methods=['GET', 'POST'])
@login_required
def trim_video():
    form = VideoUploadForm()
    video_url=None

    if form.validate_on_submit():
        video = form.photo.data
        trim_start = int(request.form.get('trim_start'))
        trim_end = int(request.form.get('trim_end'))

        # Thêm điều kiện kiểm tra
        if trim_start < 0 or trim_end <= trim_start:
            flash('Invalid trim start or trim end values.', 'error')
            return render_template('trim_video.html', form=form, video_url=video_url)

        video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(video.filename))
        video.save(video_path)

        # Kiểm tra thời gian video
        clip = VideoFileClip(video_path)
        video_duration = clip.duration

        if trim_end > video_duration:
            flash('Trim end time exceeds video duration.', 'error')
            return render_template('trim_video.html', form=form, video_url=video_url)

        video_url = videoedit.trim_video_function(video_path, trim_start, trim_end)

    return render_template('imgedit_trim_video.html', form=form, video_url=video_url)

@main.route('/merge_video', methods=['GET', 'POST'])
@login_required
def merge_video():
    form = MultiVideoUploadForm()
    video_url = ''
    if form.validate_on_submit():
        video1 = form.video1.data
        video2 = form.video2.data

        video1_path = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(video1.filename))
        video2_path = os.path.join(current_app.config["UPLOAD_FOLDER"], secure_filename(video2.filename))

        video1.save(video1_path)
        video2.save(video2_path)

        video_url = videoedit.merge_video_function(video1_path, video2_path)

    return render_template('imgedit_merge_video.html', form=form, video_url=video_url)
