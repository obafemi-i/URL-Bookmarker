from datetime import datetime
import string
import random
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship('Bookmark', backref='user')

    def __repr__(self) -> str:
        return f'User >> {self.username}'
    
class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(), nullable=True)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, onupdate=datetime.now())

    
    def generate_short_chars(self):
        characters = string.digits + string.ascii_letters
        picked_chars = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=picked_chars).first()  # checks if the value of 'picked_chars' exists in the database
        if link:
            self.generate_short_chars() # if it exists, recursively calls the function to generate another 3 digit code
        else:
            return picked_chars  # exits the function cause a unique code has been generated 

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.short_url = self.generate_short_chars()

    def __repr__(self) -> str:
        return f'bookamrk >> {self.URL}'