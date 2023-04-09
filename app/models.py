from app import db
from datetime import datetime

class Entry_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posttype = db.Column(db.Integer, index=True) # 0 means Summarize from Text, 1 means from URL; 2 for PDF File Upload
    url = db.Column(db.String(2048), index=True) # "0" for Summarize from Text; 1 for URL string;
    text2summarize = db.Column(db.String(214748364), index=True)
    text2summarize_hash = db.Column(db.String(64), index=True)  # Added new column for hash value
    openAIsummary = db.Column(db.String(214748), index=True)

    def __repr__(self):
        return '<Entry_Posts {}>'.format(self.id)

# Write a new Class for Table to store User information from linkedin_bp of Flask-Dance
class oAuthUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    linkedin_id = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    name = db.Column(db.String(120), index=True)
    picture = db.Column(db.String(120), index=True)
    token = db.Column(db.String(120), index=True)

    def __repr__(self):
        return '<oAuthUser {}>'.format(self.id)
    
#Write a new Class for Table to store the Entry_Posts id and oAuthUser id
class Entry_Posts_oAuthUsers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    entry_post_id = db.Column(db.Integer, index=True)
    oAuthUser_id = db.Column(db.Integer, index=True)

    def __repr__(self):
        return '<Entry_Posts_oAuthUsers {}>'.format(self.id)