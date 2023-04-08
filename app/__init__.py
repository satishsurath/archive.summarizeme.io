import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize the session
Session(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

from app import routes, models
from app.models import Entry_Post

# ---------------  Configure logging --------------- #
# This is the logging configuration for the app
# Check if the app is in debug mode
if not app.debug:
    # Set up email error logging
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='SummarizeMe.io Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        email_handler.setFormatter(SessionDataFormatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]\n'
            'Request data: %(request_data)s\n'
            'Session data: %(session_data)s\n'
            'User Agent: %(user_agent)s\n'
        ))
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
file_handler = RotatingFileHandler(
    'logs/summarizeme.log', 
    maxBytes=10240, 
    backupCount=10
)
file_handler.setFormatter(SessionDataFormatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]\n'
    'Request data: %(request_data)s\n'
    'Session data: %(session_data)s\n'
    'User Agent: %(user_agent)s\n'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)


    app.logger.setLevel(logging.INFO)
    app.logger.info('--------SummarizeMe startup-----------')


# ---------------  shell context processor --------------- #
# This is the shell context processor to make the database available in the shell
# to run the shell, type: flask shell eg. >flask db init
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry_Post': Entry_Post}