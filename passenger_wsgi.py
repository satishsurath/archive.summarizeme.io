import sys, os
from dotenv import load_dotenv 
load_dotenv()
INTERP = os.path.join(os.environ['HOME'], 'summerize4me', 'venv', 'bin', 'python3')
if (os.environ.get('INTERP')):
        INTERP = os.environ.get('INTERP')

if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from flask import Flask
application = Flask(__name__)
@application.route('/')
def index():
    return 'Check back soon... '

