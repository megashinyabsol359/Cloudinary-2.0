from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

import face_recognition
import cv2

from .models import User, Track
from . import db

import time

import base64
import numpy as np

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    # code login
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()
    
    is_user_login = Track.query.filter_by(email=email,is_login=True).first()
    if is_user_login:
        flash('Tài khoản đang đăng nhập ở nơi khác')
        return redirect(url_for('auth.login')) # if the user already login somewhere else
    
    # kiểm tra user tồn tại trong database
    # kiểm tra password với hash
    if not user or not check_password_hash(user.password, password):
        flash('Vui lòng kiểm tra lại thông tin đăng nhập')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # nếu đúng hết ở trên thì đăng nhập người dùng
    login_user(user, remember=remember)
    new_login = Track(email=email, time_login=time.ctime())
    db.session.add(new_login)
    db.session.commit()
    
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    # code lấy thông tin từ người dùng
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')

    user = User.query.filter_by(email=email).first() # kiểm tra người dùng trong database qua email

    if user: # nếu tìm ra người dùng thì quay về trang signup dùng gmail khác
        flash('Tài khoản sử dụng Email này đã tồn tại')
        return redirect(url_for('auth.signup'))
    if len(password) < 8 or len(password) > 50:# nếu password ko hợp lệ
        flash('Mật khẩu phải có từ 8 đến 50 ký tự')
        return redirect(url_for('auth.signup'))
    if password != password_confirm:# nếu password và nhập lại ko khớp
        flash('Mật khẩu và xác nhận mật khẩu không khớp')
        return redirect(url_for('auth.signup'))

    # nếu đúng hết thì tạo tài khoản mới, hash password
    new_user = User(email=email, name=name, password=generate_password_hash(password))

    # thêm vào database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    user = User.query.filter_by(id=current_user.get_id()).first() # kiểm tra người dùng trong database qua email
    login_log = Track.query.filter_by(email=user.email, is_login=True).first() 
    login_log.is_login = False
    login_log.time_logout = time.ctime()
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/register_face')
@login_required
def register_face():
    return render_template('register_face.html')

@auth.route('/register_face', methods=['POST'])
@login_required
def register_face_post():
    user = User.query.filter_by(id=current_user.get_id()).first()
    password = request.form.get('password')
    
    if not check_password_hash(user.password, password):
        flash('Mật khẩu không đúng!', 'danger')
        return redirect(url_for('auth.register_face'))
    
    uploaded_image = request.files['image']

    if uploaded_image:# kiểm tra có hình chưa
        image = face_recognition.load_image_file(uploaded_image)
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 1:  # Chỉ xử lý ảnh có một khuôn mặt
            face_encoding = face_recognition.face_encodings(image)[0]

            # Cắt hình ảnh khuôn mặt
            top, right, bottom, left = face_locations[0]
            face_image = image[top:bottom, left:right]

            # Lưu hình ảnh khuôn mặt đã cắt xuống cơ sở dữ liệu
            user.face_encoding = face_encoding
            user.face_image = cv2.imencode('.jpg', face_image)[1].tobytes()  # Chuyển hình ảnh thành dữ liệu nhị phân

            db.session.commit()
            flash('Đăng ký khuôn mặt thành công!', 'success')
            return redirect(url_for('auth.register_face'))
        else:
            flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
    else:
        flash('Vui lòng tải lên một ảnh.', 'danger')

    return redirect(url_for('auth.register_face'))

@auth.route('/login_face')
def login_face():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    return render_template('login_face.html')

@auth.route('/login_face', methods=['POST'])
def login_face_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first() # kiểm tra tài khoản trong database qua email
    remember = True if request.form.get('remember') else False
    
    is_user_login = Track.query.filter_by(email=email,is_login=True).first()
    if is_user_login:
        flash('Tài khoản đang đăng nhập ở nơi khác')
        return redirect(url_for('auth.login_face')) # if the user already login somewhere else

    uploaded_image = request.files['image']
        
    if not user: # nếu tìm ra người dùng thì quay về trang signup dùng gmail khác
        flash('Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.')
        return redirect(url_for('auth.login_face'))

    if not uploaded_image:# kiểm tra có hình chưa
        flash('Vui lòng tải lên một ảnh.', 'danger')
        return redirect(url_for('auth.login_face'))
        
    image = face_recognition.load_image_file(uploaded_image)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) != 1:
        flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
        return redirect(url_for('auth.login_face'))
    face_encoding = face_recognition.face_encodings(image)[0]
    
    if user.face_encoding is None or not face_recognition.compare_faces([user.face_encoding], face_encoding)[0]:
        flash('Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.', 'danger')
        return redirect(url_for('auth.login_face'))
        
    login_user(user, remember=remember) # Sau khi qua hết thì đăng nhập user
    return redirect(url_for('main.profile'))  # Chuyển hướng sau khi xác thực bằng khuôn mặt

@auth.route('/register_cam')
@login_required
def register_cam():
    error = request.args.get('error')
    return render_template('register_cam.html',error=error)

@auth.route('/register_cam', methods=['POST'])
@login_required
def register_cam_post():
    user = User.query.filter_by(id=current_user.get_id()).first()
    password = request.json['password']
    
    if not check_password_hash(user.password, password):
        error = 'Mật khẩu không đúng!'
        return redirect(url_for('auth.register_cam', error=error))
    
    # Nhận dữ liệu hình ảnh từ yêu cầu POST
    data_url = request.json['image']

    # Loại bỏ phần đầu của chuỗi dữ liệu URL (prefix "data:image/jpeg;base64,")
    img_data = data_url.split(',')[1]

    # Chuyển đổi dữ liệu hình ảnh từ base64 sang binary
    binary_data = base64.b64decode(img_data)

    jpg_as_np = np.frombuffer(binary_data, dtype=np.uint8)
    #image_buffer = cv2.imdecode(jpg_as_np, flags=1)
    
    image = cv2.imdecode(jpg_as_np, flags=1)
    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 1:  # Chỉ xử lý ảnh có một khuôn mặt
        face_encoding = face_recognition.face_encodings(image)[0]

        # Cắt hình ảnh khuôn mặt
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]

        # Lưu hình ảnh khuôn mặt đã cắt xuống cơ sở dữ liệu
        user.face_encoding = face_encoding
        user.face_image = cv2.imencode('.jpg', face_image)[1].tobytes()  # Chuyển hình ảnh thành dữ liệu nhị phân

        db.session.commit()
        error = 'Đăng ký khuôn mặt thành công!'
        return redirect(url_for('auth.register_cam', error=error))
    else:
        error = 'Vui lòng trong facecam chỉ chứa duy nhất một khuôn mặt.'

    return redirect(url_for('auth.register_cam', error=error))


@auth.route('/login_cam')
def login_cam():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    error = request.args.get('error')
    return render_template('login_cam.html',error=error)

@auth.route('/login_cam', methods=['POST'])
def login_cam_post():
    if current_user.is_authenticated:
        return redirect(url_for('main.index')) 
    
    
    # Nhận dữ liệu hình ảnh từ yêu cầu POST
    image_url = request.json['image']
    
    email = request.json['email']
    
    remember = True if request.json['remember'] else False  
    
    is_user_login = Track.query.filter_by(email=email,is_login=True).first()
    if is_user_login:
        flash('Tài khoản đang đăng nhập ở nơi khác')
        error = 'Tài khoản đang đăng nhập ở nơi khác'
        return redirect(url_for('auth.login_cam', error=error)) # if the user already login somewhere else
    
    # Loại bỏ phần đầu của chuỗi dữ liệu URL (prefix "data:image/jpeg;base64,")
    img_data = image_url.split(',')[1]

    # Chuyển đổi dữ liệu hình ảnh từ base64 sang binary
    binary_data = base64.b64decode(img_data)

    jpg_as_np = np.frombuffer(binary_data, dtype=np.uint8)    
    image = cv2.imdecode(jpg_as_np, flags=1)


    user = User.query.filter_by(email=email).first() # kiểm tra tài khoản trong database qua email
        
    if not user: # nếu tìm ra người dùng thì quay về trang signup dùng gmail khác
        flash('Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.')
        error = 'Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.'
        return redirect(url_for('auth.login_cam', error=error))

    face_locations = face_recognition.face_locations(image)

    if len(face_locations) != 1:
        flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
        error = 'Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.'
        return redirect(url_for('auth.login_cam', error=error))
    face_encoding = face_recognition.face_encodings(image)[0]
    
    if user.face_encoding is None or not face_recognition.compare_faces([user.face_encoding], face_encoding)[0]:
        flash('Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.', 'danger')
        error = 'Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại thông tin đăng nhập.'
        return redirect(url_for('auth.login_cam', error=error))
        
    
    login_user(user, remember=remember) # Sau khi qua hết thì đăng nhập user
    return redirect(url_for('main.profile'))  # Chuyển hướng sau khi xác thực bằng khuôn mặt

@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.filter_by(id=current_user.get_id()).first()

        if not check_password_hash(user.password, current_password):
            flash('Mật khẩu hiện tại không đúng!', 'danger')
        elif new_password != confirm_password:
            flash('Mật khẩu mới và xác nhận mật khẩu không khớp!', 'danger')
        elif len(new_password) < 8 or len(new_password) > 50:
            flash('Mật khẩu mới phải có từ 8 đến 50 ký tự!', 'danger')
        else:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Thay đổi mật khẩu thành công!', 'success')
            return redirect(url_for('main.profile'))

    return render_template('change_password.html')


