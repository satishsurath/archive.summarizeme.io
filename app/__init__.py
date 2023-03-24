from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
#from flask_login import login_user, logout_user, login_required, LoginManager, current_user

from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

#login_manager = LoginManager(app)
#login_manager.init_app(app)


from app import routes, models
from app.models import Entry_Post


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry_Post': Entry_Post}