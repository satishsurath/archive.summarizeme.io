from flask import Flask
from flask_turnstile import Turnstile

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
turnstile = Turnstile(app=app)



from app import routes