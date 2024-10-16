from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager

app = Flask(__name__)

# Create database connection object
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"]  = 'sqlite:///' + os.path.join(basedir, 'myApp.db')
app.config['SECRET_KEY'] = "bcc090e2-26b2-4c16-84ab-e766cc644320"

db = SQLAlchemy(app)
login_manager = LoginManager(app)

login_manager.login_view = "login"