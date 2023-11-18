from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import cv2
import numpy as np
import face_recognition

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def generate_unique_token():
    import secrets
    return secrets.token_hex(16)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    face_encoding = db.Column(db.PickleType)
    face_image = db.Column(db.LargeBinary)
    token = db.Column(db.String(32), unique=True, nullable=True)

# Routes và views
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Kiểm tra độ dài tên đăng nhập và mật khẩu
        if len(username) < 6 or len(username) > 20:
            flash('Tên đăng ký phải có từ 6 đến 20 ký tự.', 'danger')
        elif not username[0].isalpha():
            flash('Tên đăng ký phải bắt đầu bằng một ký tự chữ cái.', 'danger')
        elif len(password) < 8 or len(password) > 50:
            flash('Mật khẩu phải có từ 8 đến 50 ký tự.', 'danger')
        elif password != confirm_password:
            flash('Mật khẩu và xác nhận mật khẩu không khớp.', 'danger')
        elif User.query.filter_by(username=username).first():
            flash('Tên đăng ký đã tồn tại. Vui lòng chọn tên đăng ký khác.', 'danger')
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Tạo tài khoản thành công!', 'success')
            return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login_face', methods=['GET', 'POST'])
def login_face():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if 'image' in request.files:
            uploaded_image = request.files['image']

            if uploaded_image:
                image = face_recognition.load_image_file(uploaded_image)
                face_locations = face_recognition.face_locations(image)

                if len(face_locations) == 1:
                    face_encoding = face_recognition.face_encodings(image)[0]
                    if user:
                        if user.face_encoding:
                            if face_recognition.compare_faces([user.face_encoding], face_encoding)[0]:
                                session['user_id'] = user.id
                                return redirect(url_for('welcome'))  # Chuyển hướng sau khi xác thực bằng khuôn mặt
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

    return render_template('login_face.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.token is None:
                # Kiểm tra mật khẩu
                if bcrypt.check_password_hash(user.password, password):
                    # Đăng nhập thành công, cấp token cho người dùng
                    user.token = generate_unique_token()
                    db.session.commit()
                    session['user_id'] = user.id
                    return redirect(url_for('welcome'))
                else:
                    flash('Đăng nhập không thành công. Vui lòng kiểm tra thông tin đăng nhập!', 'danger')
            else:
                flash('Tài khoản này đã có người dùng đăng nhập.', 'danger')
        else:
            flash('Tài khoản không tồn tại. Vui lòng kiểm tra thông tin đăng nhập!', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        return redirect(url_for('welcome'))
    else:
        return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' in session:
        if request.method == 'POST':
            user = User.query.filter_by(id=session['user_id']).first()
            new_password = request.form['new_password']
            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password
            db.session.commit()
            flash('Mật khẩu đã được thay đổi!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('change_password.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user and user.token:  # Kiểm tra cả session và token
            return render_template('welcome.html', user=user)
    return redirect(url_for('login'))

    
# Khi người dùng chọn đăng ký khuôn mặt
@app.route('/register_face', methods=['POST'])
def register_face():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()

        if user:
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
                else:
                    flash('Vui lòng tải lên một ảnh chứa duy nhất một khuôn mặt.', 'danger')
            else:
                flash('Vui lòng tải lên một ảnh.', 'danger')

        return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            user.token = None  # Xóa token khi người dùng đăng xuất
            db.session.commit()
        session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Đặt giá trị token của tất cả tài khoản thành None
        users = User.query.all()
        for user in users:
            user.token = None
        db.session.commit()
    app.run(debug=True)
