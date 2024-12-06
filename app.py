# This imports the Flask class from the Flask library. Flask is used to create a Flask application.
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from wtforms import StringField, SelectField, PasswordField, SubmitField, TextAreaField, DateField   # Importing necessary field types
# from wtforms import   # Import SelectField for status
from wtforms.validators import DataRequired, Length, EqualTo  # Importing validators for form fields
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm  # Importing Flask-WTF for form handling
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from models import db, User, Task  


app = Flask(__name__) #initializes the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite for simplicity This line configures the database URI for the Flask application, specifying the database that SQLAlchemy should use.
# app.config dictionary for storing Flask app configurations.
# SQLALCHEMY_DATABASE_URI Specifies the type and location of the database.
# = "sqllite..." URI tells SQLAlchemy to use SQLite as the database and creates a file named tasks.db in the current directory.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# This line configures SQLAlchemy to disable event tracking in Flask applications.
# Event tracking: SQLAlchemy includes a feature to track changes to objects and emit signals.
app.secret_key = 'secret_key_0000'  # Change this in production
# .secret_key: - A built-in configuration attribute of Flask.
# A placeholder string. -Replace this with a unique, random, and secure key in a real-world application.
# Ensures security for session management in Flask applications.
db.init_app(app)  # Initialize the database

# Create the database tables when the app starts for the first time
with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redirect to the login page if a user isn't logged in


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Retrieve user by their ID
#---------------------------------------------------------------------------classes
# Define a registration form class using FlaskForm
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),  # Ensure username is not empty
        Length(min=5, max=20, message="Username must be between 5 and 20 characters.")  # Set stricter length limits
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),  # Ensure password is not empty
        Length(min=7, message="Password must be at least 7 characters long.")  # Enforce minimum length for password
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),  # Ensure confirmation is not empty
        EqualTo('password', message="Passwords must match.")  # Ensure passwords match
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AddTaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description')
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Incomplete', 'Incomplete'), ('Completed', 'Completed'), ('Running', 'Running')], default='Incomplete')
    submit = SubmitField('Add Task')

#---------------------------------------------------------------------------routes
@app.route('/') # maps the home URL / to the home function
def home():
    return "Welcome to Task Management System!"

# Route for user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Create an instance of the registration form
    if not form.validate_on_submit():
        print("Form validation errors:", form.errors)  # Debug: Print form validation errors
    if form.validate_on_submit():  # Check if the form was submitted and all validations passed
        print("Form validated!")  # Debug: Check if the form was validated successfully
        # Check if the username already exists in the database
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            print("Username already exists!")  # Debug: Check if the username exists
            flash('Username already exists. Please choose a different one.', 'danger')  # Show error message
        else:
            # If valid, create a new user object
            # new_user = User(username=form.username.data, password=form.password.data)
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')  # Hash the password
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)  # Add the new user to the database
            db.session.commit()  # Commit the session to save changes
            print("User created!")  # Debug: Check if the user is successfully added
            flash('Registration successful! You can now log in.', 'success')  # Show success message
            return redirect(url_for('dashboard'))  # Redirect to the home page
    else:
        print("Form validation failed.")  # Debug: Handle validation failures
    return render_template('register.html', form=form)  # Render the registration page

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     tasks = Task.query.filter_by(user_id=current_user.id).all()
#     return render_template('dashboard.html', tasks=tasks)

from datetime import datetime, timedelta
from flask import request

@app.route('/dashboard')
@login_required
def dashboard():
    # Get filter parameters from the request
    status_filter = request.args.get('status', 'incomplete')  # Default to 'all'
    due_date_filter = request.args.get('due_date', 'all')  # Default to 'all'

    # Base query for tasks belonging to the current user
    query = Task.query.filter_by(user_id=current_user.id)

    # Apply status filter
    if status_filter == 'completed':
        query = query.filter_by(status='Completed')
    elif status_filter == 'incomplete':
        query = query.filter_by(status='Incomplete')
    elif status_filter == 'running':
        query = query.filter_by(status='Running')

    # Apply due date filter
    if due_date_filter == 'today':
        today = datetime.today().date()
        query = query.filter(Task.due_date == today)
    elif due_date_filter == 'week':
        next_week = datetime.today().date() + timedelta(days=7)
        query = query.filter(Task.due_date.between(datetime.today().date(), next_week))
    elif due_date_filter == '15days':
        next_15_days = datetime.today().date() + timedelta(days=15)
        query = query.filter(Task.due_date.between(datetime.today().date(), next_15_days))
    elif due_date_filter == 'month':
        next_month = datetime.today().date() + timedelta(days=30)
        query = query.filter(Task.due_date.between(datetime.today().date(), next_month))

    # Execute the query to get the filtered tasks
    tasks = query.all()

    # Render the dashboard with the filtered tasks
    return render_template('dashboard.html', tasks=tasks, status_filter=status_filter, due_date_filter=due_date_filter)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):  # Simplified for demo purposes
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after login
        else:
            flash('Login Unsuccessful. Please check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)  # Get the task by ID or return a 404 error
    form = AddTaskForm()  # You can reuse the AddTaskForm for editing

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.status = form.status.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the dashboard after editing

    # Populate form with existing task data
    form.title.data = task.title
    form.description.data = task.description
    form.due_date.data = task.due_date
    form.status.data = task.status

    return render_template('add_task.html', form=form, task=task)  # Reuse the add_task.html template for editing

@app.route('/delete_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('dashboard'))  # Redirect to the dashboard after deletion

@app.route('/add_task', methods=['GET', 'POST'])
@login_required
def add_task():
    form = AddTaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data,  # Use the status from the form
            user_id=current_user.id
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect back to dashboard after adding
    return render_template('add_task.html', form=form)  # Render add task form

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))  # Redirect to home after logging out

if __name__ == '__main__': #ensures the app runs only if the script is executed directly
    app.run(debug=True) #starts the app in debug mode, allowing automatic reloading on changes.


# It runs a web server and serves a home page at / with a welcome message.

# use this if there is any issue in starting process of the app.py
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)