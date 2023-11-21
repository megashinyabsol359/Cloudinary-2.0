from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user

import face_recognition
import cv2

from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
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
    uploaded_image = request.files['image']

    if uploaded_image:
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
            redirect(url_for('main.profile'))
        else:
            flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
    else:
        flash('Vui lòng tải lên một ảnh.', 'danger')

    return redirect(url_for('auth.register_face'))

@auth.route('/login_face')
def login_face():
    return render_template('login_face.html')

@auth.route('/login_face', methods=['POST'])
def login_face_post():
    email = request.form['username']
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
    remember = True if request.form.get('remember') else False

    if 'image' in request.files:
        uploaded_image = request.files['image']

        if uploaded_image:
            image = face_recognition.load_image_file(uploaded_image)
            face_locations = face_recognition.face_locations(image)

            if len(face_locations) == 1:
                face_encoding = face_recognition.face_encodings(image)[0]
                if user:
                    print(user.face_encoding)
                    if user.face_encoding is not None:
                        if face_recognition.compare_faces([user.face_encoding], face_encoding)[0]:
                            login_user(user, remember=remember)
                            return redirect(url_for('main.profile'))  # Chuyển hướng sau khi xác thực bằng khuôn mặt
                        else:
                            flash('Xác thực bằng khuôn mặt không thành công. Vui lòng kiểm tra lại.', 'danger')
                    else:
                        flash('Tài khoản chưa được đăng ký khuôn mặt. Vui lòng đăng ký khuôn mặt.', 'danger')
                else:
                    flash('Tài khoản không tồn tại. Vui lòng kiểm tra thông tin đăng nhập!', 'danger')
            else:
                flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
        else:
            flash('Vui lòng tải lên một ảnh.', 'danger')

    # if the above check passes, then we know the user has the right credentials
    #flash('Email address already exists')
    return redirect(url_for('auth.login_face'))

