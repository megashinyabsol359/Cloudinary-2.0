from flask import Blueprint, render_template, send_from_directory, url_for, current_app, request, Response
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from . import db
from . import imgedit

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

@main.route('/takeimage', methods=['POST'])
def takeimage():
    # Nhận dữ liệu hình ảnh từ yêu cầu POST
    data_url = request.json['image']

    # Loại bỏ phần đầu của chuỗi dữ liệu URL (prefix "data:image/jpeg;base64,")
    img_data = data_url.split(',')[1]

    # Chuyển đổi dữ liệu hình ảnh từ base64 sang binary
    binary_data = base64.b64decode(img_data)

    # Lưu hình ảnh vào thư mục static/images với tên duy nhất và định dạng jpg
    image_name = f'image.jpg'
    image_path = os.path.join(image_name)
    with open(image_path, 'wb') as f:
        f.write(binary_data)

    print(f'Image saved at: {image_path}')

    return Response(status=200)


@main.route('/RGBtoGray', methods = ['GET', 'POST'])
@login_required
def RGBtoGray():
    form = UploadForm()
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
    form = UploadForm()
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
    form = UploadForm()
    if form.validate_on_submit():
        x1 = int(request.form.get('x1'))
        x2 = int(request.form.get('x2'))
        y1 = int(request.form.get('y1'))
        y2 = int(request.form.get('y2'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = imgedit.crop(filename, file_url, x1, x2, y1, y2)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    print(file_url)
    return render_template('imgedit_crop.html', form = form, file_url = file_url, face_file_url = face_file_url)

@main.route('/rotate', methods = ['GET', 'POST'])
@login_required
def rotate():
    form = UploadForm()
    if form.validate_on_submit():
        degree = int(request.form.get('degree'))
        x = int(request.form.get('x'))
        y = int(request.form.get('y'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = imgedit.rotate(filename, file_url, degree, x, y)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    return render_template('imgedit_rotate.html', form = form, file_url = file_url, face_file_url = face_file_url)

@main.route('/resize', methods = ['GET', 'POST'])
@login_required
def resize():
    form = UploadForm()
    if form.validate_on_submit():
        size = int(request.form.get('size'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = imgedit.resize(filename, file_url, size)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    return render_template('imgedit_resize.html', form = form, file_url = file_url, face_file_url = face_file_url)

@main.route('/resize', methods = ['GET', 'POST'])
@login_required
def hsv():
    form = UploadForm()
    if form.validate_on_submit():
        h = int(request.form.get('hue'))
        s = int(request.form.get('saturation'))
        l = int(request.form.get('light'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        face_filename = imgedit.hsv(filename, file_url, h, s, l)
        face_file_url = url_for('main.get_file', filename=face_filename)
    else:
        file_url = None
        face_file_url = None
    return render_template('imgedit_resize.html', form = form, file_url = file_url, face_file_url = face_file_url)


# @main.route('/effect_tools', methods = ['GET', 'POST'])
# @login_required
# def effect_tools():
#     form = UploadForm()
#     if form.validate_on_submit():
#         filename = photos.save(form.photo.data)
#         file_url = url_for('main.get_file', filename=filename)
#         face_filename = imgedit.effect_tools(filename, file_url)
#         face_file_url = url_for('main.get_file', filename=face_filename)
#     else:
#         file_url = None
#         face_file_url = None
#     return render_template('effect_tools.html', form = form, file_url = file_url, face_file_url = face_file_url)
