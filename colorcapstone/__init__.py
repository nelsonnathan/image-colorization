from flask import Flask
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_nav.elements import Navbar, Separator, Subgroup, View
from flask_nav import Nav
from colorcapstone.models import db
import colorcapstone.key_configuration as keys

app = Flask(__name__)

app.config['SECRET_KEY'] = keys.SECRET_KEY
app.config['SECRET_KEY'] = keys.SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


bootstrap = Bootstrap(app)

ENV = 'dev'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{keys.PSQLPass}@localhost/colorization'

db.init_app(app)
migrate = Migrate(app, db)

nav = Nav(app)


def unauth_navbar():
    navbar = Navbar(title='colorization')
    navbar.items = [View('Register', 'register'), View('Sign In', 'login')]

    return navbar


nav.register_element('unauth', unauth_navbar)


def auth_navbar():
    navbar = Navbar(title='colorization')
    navbar.items = []
    navbar.items.append(
        Subgroup('Profile',
                 View('Upload', 'upload'),
                 View('New Upload', 'photos'),
                 View('Photo Library', 'library')
                 )
    ),
    navbar.items.append(View('Sign Out', 'logout'))

    return navbar


nav.register_element('auth', auth_navbar)

from colorcapstone import routes