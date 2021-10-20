from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(128), unique=True)
    email = db.Column(db.VARCHAR(128), unique=True)
    password = db.Column(db.VARCHAR(128))
    uploads = db.relationship('Uploads', backref='user')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __repr__(self):
        return f"{self.username}:{self.email}:{self.password}:{self.uploads}"


class Uploads(db.Model):
    __tablename__ = 'uploads'
    id = db.Column(db.Integer, primary_key=True)
    bw_image_url = db.Column(db.VARCHAR(512))
    color_image_url = db.Column(db.VARCHAR(512))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, bw_image_url, color_image_url, user_id):
        self.bw_image_url = bw_image_url
        self.color_image_url = color_image_url
        self.user_id = user_id

    def __repr__(self):
        return f"{self.bw_image_url}:{self.color_image_url}:{self.user_id}"