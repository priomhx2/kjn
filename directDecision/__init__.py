import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail


directDecision= Flask(__name__)

# specifies where the database is located
directDecision.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# file on the database system is created in the project directory alongside python module
directDecision.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# database created by an instance, which is passed through the applciation as an argument
db = SQLAlchemy(directDecision)
bcrypt = Bcrypt (directDecision)



login_manager=LoginManager(directDecision)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
directDecision.config['MAIL_SERVER'] = 'smtp.gmail.com'
directDecision.config['MAIL_PORT'] = 587
directDecision.config['MAIL_USE_TLS'] = True
directDecision.config['MAIL_USERNAME'] = 'decisiondirect@gmail.com'
directDecision.config['MAIL_PASSWORD'] = 'Thomas098.'
mail = Mail(directDecision)

from directDecision import routes
