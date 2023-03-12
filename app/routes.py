from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Check back soon... and Hello, World!"