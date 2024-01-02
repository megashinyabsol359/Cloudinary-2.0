from flask import Blueprint, render_template, send_from_directory, url_for, current_app, request, Response, send_file, jsonify
from flask_login import login_required, current_user
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField
from . import db
from . import imgedit
from . import videoedit
from . import photos, videos
from moviepy.editor import VideoFileClip
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

class UploadForm(FlaskForm):
    photo = FileField(
        validators=[
            #FileAllowed((photos, videos), 'Only images or videos are allowed.'),
            FileAllowed(photos, 'Only images or videos are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    submit = SubmitField('Upload')

class MultiVideoUploadForm(FlaskForm):
    video1 = FileField(
        validators=[
            FileAllowed(['mp4'], 'Only mp4 videos are allowed.'),
            FileRequired('File field should not be empty.')
        ]
    )
    video2 = FileField(
        validators=[
            FileAllowed(['mp4'], 'Only mp4 videos are allowed.'),
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
    form = UploadForm()
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
    form = UploadForm()
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
    form = UploadForm()
    if form.validate_on_submit():
        h = int(request.form.get('hue'))
        s = int(request.form.get('saturation'))
        l = int(request.form.get('light'))
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        hsv_filename = imgedit.hsv(filename, file_url, h, s, l)
        hsv_file_url = url_for('main.get_file', filename=hsv_filename)
    else:
        file_url = None
        hsv_file_url = None
    return render_template('imgedit_hsv.html', form = form, file_url = file_url, hsv_file_url = hsv_file_url)

@main.route('/trim_video', methods=['GET', 'POST'])
@login_required
def trim_video():
    uploaded_videos = [filename for filename in os.listdir(current_app.config["UPLOAD_FOLDER"])]
    return render_template('trim_video.html', uploaded_videos=uploaded_videos)

@main.route('/upload_video', methods=['POST'])
@login_required
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
@login_required
def trim_video_edit():
    try:
        videofile = request.json['videofile']
        
        # Kiểm tra xem videofile có giá trị không
        if videofile is None:
            raise ValueError("Videofile is not provided")

        trim_start = int(request.json['trim_start'])
        trim_end = int(request.json['trim_end'])
        trimmed_filename = request.json.get('trimmed_filename', '')  # Lấy giá trị hoặc trả về rỗng nếu không có giá trị

        # Nếu trimmed_filename là rỗng, sử dụng tên file gốc + "_trim"
        if not trimmed_filename:
            filename, file_extension = os.path.splitext(videofile)
            trimmed_filename = f"{filename}_trim{file_extension}"

        # Get the duration of the video
        video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], videofile)
        clip = VideoFileClip(video_path)
        video_duration = clip.duration

        # Check if the end time is greater than the video duration
        if trim_end > video_duration:
            return {
                "status": "error",
                "message": "End time is greater than the duration of the video",
            }

        trimmed_videopath = videoedit.trim_video_function(videofile, trim_start, trim_end, trimmed_filename)
        return {
            "status": "success",
            "message": "Video edited successfully",
            "trimmed_videopath": trimmed_videopath
        }
    except Exception as e:
        return {
            "status": "error",
            "message": "Video edit failure: " + str(e),
        }

@main.route('/playback/<filename>')
@login_required
def playback(filename):
    video_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    return send_file(video_path)

@main.route('/object_detection', methods = ['GET', 'POST'])
@login_required
def object_detection():
    form = UploadForm()
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('main.get_file', filename=filename)
        gray_filename = imgedit.object_detection(filename, file_url)
        gray_file_url = url_for('main.get_file', filename=gray_filename)
    else:
        file_url = None
        gray_file_url = None
    return render_template('imgedit_object_detection.html', form = form, file_url = file_url, gray_file_url = gray_file_url)

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

    return render_template('merge_video.html', form=form, video_url=video_url)
