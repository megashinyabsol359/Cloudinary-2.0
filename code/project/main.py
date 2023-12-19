from flask import Blueprint, render_template, send_from_directory, url_for, current_app, request, Response, send_file, jsonify
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from . import db
from . import imgedit
from . import videoedit
from flask_cors import CORS
from moviepy.editor import VideoFileClip

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
    return render_template('imgedit_crop.html', form = form, file_url = file_url, crop_file_url = face_file_url)

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
    return render_template('imgedit_rotate.html', form = form, file_url = file_url, rotate_file_url = face_file_url)

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
    return render_template('imgedit_resize.html', form = form, file_url = file_url, resize_file_url = face_file_url)

@main.route('/hsv', methods = ['GET', 'POST'])
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








@main.route('/trim_video', methods = ['GET', 'POST'])
def trim_video():
    return render_template('trim_video.html')

@main.route('/uploads', methods=['GET'])
def get_uploaded_videos():
    uploaded_videos = [filename for filename in os.listdir(current_app.config["UPLOAD_FOLDER"])]
    return jsonify(uploaded_videos)

@main.route('/clips/<filename>')
def render_clip(filename):
    return send_file(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))

@main.route('/playback/<filename>')
def playback(filename):
    video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    # You may want to add additional security checks here before sending the file
    # For example, check user authentication, permissions, etc.

    return send_file(video_path)

@main.route('/upload_video', methods=['POST'])
def upload_video():
    if not os.path.exists(current_app.config["UPLOAD_FOLDER"]):
        os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

    try:
        videofile = request.files['videofile']
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], videofile.filename)
        videofile.save(filepath)
        return {"filename": videofile.filename}
    except FileNotFoundError:
        return {"error": "File not found"}

@main.route('/edit_video/trim', methods=['POST'])
def trim_video_edit():
    try:
        videofile = request.json['videofile']
        trim_start = int(request.json['trim_start'])
        trim_end = int(request.json['trim_end'])
        trimmed_filename = request.json['trimmed_filename']

        # Append the video extension (e.g., ".mp4") to the filename
        trimmed_filename_with_extension = f"{trimmed_filename}.mp4"

        edited_videopath = trim_video_function(videofile, trim_start, trim_end, trimmed_filename_with_extension)
        return {
            "status": "success",
            "message": "video edit success",
            "edited_videopath": edited_videopath
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "video edit failure: " + str(e),
        }

def trim_video_function(videofile, start_time, end_time, trimmed_filename):
    clip = VideoFileClip(os.path.join(current_app.config["UPLOAD_FOLDER"], videofile))
    trimmed_filename_with_extension = f"{trimmed_filename}"
    trimpath = os.path.join(current_app.config["UPLOAD_FOLDER"], trimmed_filename_with_extension)
    trimmed_clip = clip.subclip(start_time, end_time)
    trimmed_clip.write_videofile(trimpath)
    return trimpath