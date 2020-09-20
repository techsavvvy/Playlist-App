from flask import Flask
import flask_whooshalchemyplus
from flask_whooshalchemyplus import index_all
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sasidharan123!'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['WHOOSH_BASE']='/tmp/whoosh'

UPLOAD_FOLDER = '/audio'
ALLOWED_EXTENSIONS = {'mp3'}
WTF_CSRF_ENABLED = False

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.playlist.views import playlist
from app.usermgmt.views import usermgmt

app.register_blueprint(usermgmt, url_prefix='/')
app.register_blueprint(playlist, url_prefix='/')

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()