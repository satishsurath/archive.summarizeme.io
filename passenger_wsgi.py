import sys, os
INTERP = os.path.join(os.environ['HOME'], 'summarizeme.io', 'venv', 'bin', 'python3')

#If we are not in Production 
# Or Development Mode
# Or Staging Mode 
# - then it loads the Python Path from the .env file

if os.environ['HOME'] != '/home/dh_hjy3j9' and os.environ['HOME'] != '/home/dh_wagsu9/' and os.environ['HOME'] != '/home/dh_kzhw5x':
    from dotenv import load_dotenv
    load_dotenv()
    if (os.environ.get('INTERP')):
        INTERP = os.environ.get('INTERP')


if sys.executable != INTERP:
        os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())



from flask import Flask
application = Flask(__name__)
sys.path.append('app')
from app import app as application

