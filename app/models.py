"""
Contains all database models.

One to many relationships:
Deck to Card (one deck can have many cards)
User(owner) to Card (each card, class, and deck has one user who owns it)
User(owner) to Class
User(owner) to Deck

Many to many relationships:
User to Class (one user can join many classes, one class can have many users)
Class to Card
"""

# Third party imports
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# Local application imports
from . import db, login_manager

# flask_login


@login_manager.user_loader
def load_user(user_id):
    """
    This callback is used to reload the user object from the user ID stored
    in the session. It is required by flask_login.
    """
    return User.query.get(int(user_id))

# Association tables


UserClasses = db.Table('UserClasses',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'))
)

CardClasses = db.Table('CardClasses,'
    db.Column('card_id', db.Integer, db.ForeignKey('card.id')),
    db.Column('class_id', db.Integer, db.ForeignKey('class.id'))
)

# Class models


class User(UserMixin, db.Model):
    """ Creates User table """
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(40), unique=True)
    password_hash = db.Column(db.String(128))
    # A user can own multiple decks, cards, and classes (one to m any)
    decks = db.relationship('Deck', backref='owner')
    cards = db.relationship('Card', backref='owner')
    classes = db.relationship('Class', backref='owner')
    # Many to many: classes to users
    user_classes = db.relationship('Class',
                                   secondary=UserClasses,
                                   backref=db.backref('classes'))
                                   # user.classes will display classes

    def __init__(self, first_name, last_name, email, password_hash):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password_hash = password_hash

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<ID: {}, {}, {}>'.format(self.id,
                                         self.last_name,
                                         self.first_name)


class Deck(db.Model):
    """ Creates Deck table """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    # Every deck is owned by one user
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # A deck can have multiple cards (one to many)
    cards = db.relationship('Card', backref='deck')

    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def list_cards(self, an_owner_id):
        cards = Card.query.filter_by(owner_id=an_owner_id).all()
        return cards

    def __repr__(self):
        owner_name = self.owner.first_name + " " + self.owner.last_name
        return '<ID: {}, Name: {}, Owner: {}>'.format(self.id,
                                                      self.name,
                                                      owner_name)


class Card(db.Model):
    """ Creates Card table """
    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.String(1200))
    back = db.Column(db.String(1200))
    # Every card belongs to one deck
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'))
    # Every card is owned by one user
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, front, back, deck, owner):
        self.front = front
        self.back = back
        self.deck = deck
        self.owner = owner

    def __repr__(self):
        owner_name = self.owner.first_name + " " + self.owner.last_name
        return '<ID: {}, Front: {}, Back: {}, Deck: {}>'.format(self.id,
                                                                self.front,
                                                                self.back,
                                                                self.deck
                                                                owner_name)


class Class(db.Model):
    """ Creates Class table """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(128))
    # Every class is owned by one user
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Many to many: classes to cards
    card_classes = db.relationship('Card',
                                   secondary=CardClasses,
                                   backref=db.backref('cards'))
                                   # class.cards will display cards

    def __init__(self, name, password_hash, owner):
        self.name = name
        self.password_hash = password_hash
        self.owner = owner

    def __repr__(self):
        owner_name = self.owner.first_name + " " + self.owner.last_name
        return '<ID: {}, Name: {}, Owner: {}>'.format(self.id,
                                                      self.name,
                                                      owner_name)
