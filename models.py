from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy # imports the SQLAlchemy library for Flask.
# SQLAlchemy is an Object Relational Mapper (ORM) that simplifies database interactions by allowing you to:

# Define database tables as Python classes (models).
# Perform CRUD operations without writing raw SQL queries.

db = SQLAlchemy() #Initializes the SQLAlchemy instance, which handles database connections and operations

class User(UserMixin, db.Model):  # Inherit from UserMixin  # defines a model in SQLAlchemy. A model represents a table in a database, and each instance of the model corresponds to a row in that table.
# This is the name of the Python class, which will also be the name of the table 
# This is a base class provided by SQLAlchemy. Inheriting from db.Model tells SQLAlchemy that this class should be treated as a database model.
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Incomplete')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)