from .app import db
import yaml
import os
from flask_login import UserMixin
from .app import login_manager

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float)
    title = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(255))  # URL de l'image
    purchase_url = db.Column(db.String(255))  # URL pour acheter le livre
    author_id = db.Column(db.Integer, db.ForeignKey("author.id"))
    author = db.relationship("Author", backref=db.backref("books", lazy="dynamic"))

def get_all_authors():
    return Author.query.all()


def get_sample():
    return Book.query.limit(10).all()

def get_book(book_id):
    return Book.query.get(book_id)

def get_author(id):
    return Author.query.get(id)

class User(db.Model, UserMixin):
    username = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(64))

    def get_id(self):
        return self.username

    @login_manager.user_loader
    def load_user(username):
        return User.query.get(username)