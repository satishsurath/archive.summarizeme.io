from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app import routes, models
from app.models import Entry_Post


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry_Post': Entry_Post}