from Packages import app
from flask import render_template,redirect,url_for,flash,request
from functools import wraps
from Packages.models import Event,User,Mentee,Mentor,Group
from Packages import admin,db
from Packages.admin import ModelView,UserAdminView
from Packages.forms import RegisterForm,LoginForm,GroupCreationForm
from flask_login import login_user, login_required,current_user,logout_user
from Packages.func import process 


admin.add_view(UserAdminView(User, db.session))
admin.add_view(ModelView(Event, db.session))
admin.add_view(ModelView(Mentor,db.session))
admin.add_view(ModelView(Mentee,db.session))
admin.add_view(ModelView(Group,db.session))

def mentor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Mentor':
            # Redirect to a suitable page or return an error message
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def h1():
    return render_template('home.html')

@app.route('/cal')
@login_required
def cal():
    events = Event.query.all()
    return render_template('calendar.html',events =events)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        return redirect(url_for('login_page'))
    if form.errors != {}: #If there are not errors from the validations
        for err_msg in form.errors.values():
            print(f'There was an error with creating a user: {err_msg}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('h1'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/addgrp', methods=['GET', 'POST'])
@login_required
@mentor_required
def addgrp():
    form = GroupCreationForm()
    # Fetch the list of mentees for the mentor
    mentor = Mentor.query.filter_by(user_id=current_user.id).first()
    mentees = Mentee.query.all()

    # Populate the mentees field choices
    form.mentees.choices = [(str(mentee.id), mentee.name) for mentee in mentees]

    if form.validate_on_submit():
        selected_mentee_ids = form.mentees.data
        selected_mentees = Mentee.query.filter(Mentee.id.in_(selected_mentee_ids)).all()

        group_name = form.name.data
        group = Group(name=group_name, mentor=mentor)
        group.mentees.extend(selected_mentees)

        db.session.add(group)
        db.session.commit()

        return redirect(url_for('h1'))

    return render_template('addgrp.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("h1"))


from werkzeug.utils import secure_filename

@app.route('/upload', methods=['GET', 'POST'])
def upload_transcript():
    if request.method == 'POST':
        # Check if the 'transcript' file was uploaded
        if 'transcript' not in request.files:
            return 'No file uploaded'

        file = request.files['transcript']

        # Check if a file was selected
        if file.filename == '':
            return 'No file selected'

        # Securely save the file
        filename = secure_filename(file.filename)
        file.save(filename)

        # Process the transcript file
        result = process_transcript(filename)

        # Pass the result to the template for display
        return render_template('result.html', result=result)

    return render_template('trans.html')

def process_transcript(filename):
    # Read the file and extract its text content
    with open(filename, 'r') as file:
        text = file.read()

    summ=process(text)
    # Perform any additional processing or analysis on the text
    # For example, you could apply NLP techniques, perform text mining, etc.

    return summ

    
    