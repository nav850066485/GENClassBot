from Packages import db, login_manager
from sqlalchemy_utils import URLType
from Packages import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(length=60), nullable=False)
    role = db.Column(db.String(20), default='Mentee')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = 'Mentee'  # Set the default role to 'Mentee'
        self.create_mentee()

    def create_mentee(self):
        if self.role == 'Mentee':
            mentee = Mentee(name=self.username, user=self)
            db.session.add(mentee)
            db.session.commit()

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=20), nullable=False)
    Start = db.Column(db.DateTime(), nullable=False)
    End = db.Column(db.DateTime(), nullable=False)
    Url_session = db.Column(db.String(), nullable=False)
    Url = db.Column(URLType(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)

    def __repr__(self):
        return f'Item {self.name}'

class Mentee(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('mentee', uselist=False))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))


class Mentor(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name= db.Column(db.String(length=20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('mentor', uselist=False))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user.role = 'Mentor'

class Group(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=20))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor.id'))
    mentor = db.relationship('Mentor', backref=db.backref('groups', lazy='dynamic'))
    mentees = db.relationship('Mentee', backref='group', lazy='dynamic')

    def __init__(self, name, mentor):
        self.name = name
        self.mentor = mentor

    