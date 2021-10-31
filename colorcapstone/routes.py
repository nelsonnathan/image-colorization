import os
import boto3
import mimetypes

from boto3 import session
from colorcapstone import app
from flask import render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask.helpers import url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from colorcapstone.models import db, Users, Uploads
from colorcapstone.aws import s3, BUCKET_NAME

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class LoginForm(FlaskForm):
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[
                           InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[
                             InputRequired(), Length(min=8, max=80)])


class ImageUpload(FlaskForm):
    url = StringField('image url', validators=[InputRequired()])


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
@login_required
def home():
    return redirect(url_for('login'))


@app.route('/', methods=['POST'])
@login_required
def submit():
    form = ImageUpload()
    user_id = current_user.id
    file_mime_type = None
    if request.method == 'POST':
        img = request.files['file']
        if img:
            filename = secure_filename(img.filename)
            img.save(filename)
            file_mime_type = mimetypes.guess_type(filename)[0]
            s3.upload_file(
                Bucket=BUCKET_NAME,
                Filename=filename,
                Key=filename,
                ExtraArgs={'ContentType': file_mime_type}
            )

            url = f'https://{BUCKET_NAME}.s3.us-west-1.amazonaws.com/{filename}'
            new_upload = Uploads(url, None, user_id)
            db.session.add(new_upload)
            db.session.commit()

    return redirect(url_for('photos'))


@app.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    current = current_user.id
    table = db.session.query(Uploads.bw_image_url).filter(Uploads.user_id==current).all()
    new_photo = table[-1][0]
    user = db.session.query(Uploads.user_id).first()
    user_id = user[0]

    if user_id == current:
        return render_template('photos.html', new_image=new_photo)

    return redirect(url_for('upload'))

@app.route('/library', methods=['GET'])
@login_required
def library():
    current = current_user.id
    table = db.session.query(Uploads.bw_image_url).filter(Uploads.user_id==current).all()
    user = db.session.query(Uploads.user_id).first()
    user_id = user[0]

    if user_id == current:
        return render_template('library.html', new_image=table)

    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_pass = generate_password_hash(
            form.password.data, method='sha256')
        new_user = Users(username=form.username.data,
                         email=form.email.data, password=hashed_pass)
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'

    return render_template('registration.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('upload'))
    return render_template('login.html', form=form)


@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
