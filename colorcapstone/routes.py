import mimetypes
import requests

from boto3 import session
from PIL import Image
from sqlalchemy.sql.operators import exists
from colorcapstone import app, jsonify, Cache
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

url_dict = {}

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

            bw_url = f'https://{BUCKET_NAME}.s3.us-west-1.amazonaws.com/{filename}'
            
            r = requests.post(
            "https://api.deepai.org/api/colorizer",
            data={
                'image': bw_url,
            },
            headers={'api-key': '526cc8b1-8b67-40ad-8e15-394675ec5291'}
            )

            color_url = r.json()['output_url']

            sr = requests.post(
            "https://api.deepai.org/api/torch-srgan",
            data={
                'image': color_url,
            },
            headers={'api-key': '526cc8b1-8b67-40ad-8e15-394675ec5291'}
            )

            print(sr.json())

            upscaled_url = sr.json()['output_url']

            new_upload = Uploads(bw_url, upscaled_url, user_id)
            db.session.add(new_upload)
            db.session.commit()


    return redirect(url_for('photos'))


@app.route('/delete/<int:id>', methods=['GET'])
@login_required
def delete(id):
    Uploads.query.filter(Uploads.id == id).delete()
    db.session.commit()
    return jsonify({'hello': 'world'})

    
@app.route('/photos', methods=['GET', 'POST'])
@login_required
def photos():
    current = current_user.id
    table = db.session.query(Uploads.bw_image_url, Uploads.color_image_url).filter(Uploads.user_id==current).all()
    user = db.session.query(Uploads.user_id).filter(Uploads.user_id==current).first()

    if user == None:
        return redirect(url_for('upload'))
    
    user_id = user[0]

    url_index = [0, 1]
    photos = table[-1]
    photo_urls = [ photos[i] for i in url_index]
    bw_url = photo_urls[0]
    color_url = photo_urls[1]

    if user_id == current:
        return render_template('photos.html', bw_image=bw_url, color_image=color_url)
    

    return redirect(url_for('upload'))

@app.route('/library', methods=['GET'])
@login_required
def library():
    current = current_user.id
    table = db.session.query(Uploads.bw_image_url, Uploads.color_image_url, Uploads.id).filter(Uploads.user_id==current).all()
    user = db.session.query(Uploads.user_id).filter(Uploads.user_id==current).first()

    if user == None:
        url_dict.clear()
        print(url_dict)
        return redirect(url_for('upload'))

    user_id = user[0]

    url_index = [0, 1]
    photos = table[-1]
    photo_urls = [ photos[i] for i in url_index]
    bw_url = photo_urls[0]
    color_url = photo_urls[1]

    url_dict[bw_url] = bw_url
    url_dict[color_url] = color_url

    photo_id = db.session.query(Uploads.id).all()
    current_photo_id = photo_id[-1][0]

    if user_id == current:
        print('The url dictionary variable:\n', url_dict)
        print('The current photo id variable:\n', current_photo_id)
        return render_template('library.html', photos=table, id=current_photo_id)

    return redirect(url_for('upload'))



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
