from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_nav.elements import Navbar, View
from flask_nav import Nav
from colorcapstone.models import db
import colorcapstone.key_configuration as keys

app = Flask(__name__)

UPLOAD_FOLDER = 'colorcapstone/static/pictures'

app.config['SECRET_KEY'] = keys.SECRET_KEY
app.config['SECRET_KEY'] = keys.SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

bootstrap = Bootstrap(app)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{keys.PSQLPass}@localhost/colorization'

db.init_app(app)
migrate = Migrate(app, db)

nav = Nav(app)

@nav.navigation()
def mynavbar():
    return Navbar(
        'colorization',
        View('Dashboard', 'dashboard'),
        View('Sign In', 'login'),
        View('Register', 'register'),
        View('Logout', 'logout')
    )

from colorcapstone import routes