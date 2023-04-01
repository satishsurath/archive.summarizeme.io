from app import db
from datetime import datetime

class Entry_Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    posttype = db.Column(db.Integer, index=True) # 0 means Summarize from Text, 1 means from URL...
    url = db.Column(db.String(2048), index=True) # "0" for Summarize from Text; else URL string
    test2summarize = db.Column(db.String(214748364), index=True)
    test2summarize_hash = db.Column(db.String(64), index=True)  # Added new column for hash value
    openAIsummary = db.Column(db.String(214748), index=True)

    def __repr__(self):
        return '<Entry_Posts {}>'.format(self.id)
