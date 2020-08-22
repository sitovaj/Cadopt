
import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

database_name = "cadopt"
database_path = "postgres://{}:{}@{}/{}".format(
    'student', 'student', 'localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://postgres@localhost:5432/' #database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.drop_all()
    db.create_all()


'''
Cat

'''


class Cat(db.Model):
    __tablename__ = 'cats'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    birthday = Column(DateTime)
    color = Column(String)
    city = Column(String)
    image = Column(String)
    status = Column(String)
    # curator_id = Column(Integer, db.ForeignKey('curators.id'), primary_key=False)
    # curator = db.relationship("Curator", back_populates="cats")
    curator_id = db.Column(db.Integer, db.ForeignKey('curators.id'),nullable=False)

    def __init__(self, name, gender, birthday, color, city, image, status, curator_id):
    
        self.name = name
        self.gender = gender
        self.birthday = birthday        
        self.color = color
        self.city = city
        self.image = image
        self.status = status
        self.curator_id = curator_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'birthday': self.birthday,
            'color': self.color,
            'city': self.city,
            'image': self.image,
            'status': self.status,
            'curator_id': self.curator_id
        }

# Upload serializer
    def serialize_cat_bis(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'birthday': self.birthday,
            'color': self.color,
            'city': self.city,
            'image': self.image,
            'status': self.status
        }

    def serialize_cat(self):
        if self.curator:
            dict_curator = self.curator.serialize_curator_bis()
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'birthday': self.birthday,
            'color': self.color,
            'city': self.city,
            'image': self.image,
            'status': self.status,
            'curator': dict_curator
        }


'''
Curator

'''


class Curator(db.Model):
    __tablename__ = 'curators'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    legal_number = Column(String)
    phone = Column(String)
    email = Column(String)
    facebook = Column(String)
    # cats = db.relationship("Cat", cascade="all, delete-orphan", back_populates="curator", lazy=True)
    cats = db.relationship('Cat', backref='curator', lazy=True)

    def __init__(self, name, legal_number, phone, email, facebook, cats
    ):
        self.name = name
        self.legal_number = legal_number
        self.phone = phone
        self.email = email
        self.facebook = facebook
        self.cats = cats

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'legal_number': self.legal_number,
            'phone': self.phone,
            'email': self.email,
            'facebook': self.facebook,
            'cats': self.cats
        }

# curator serializer
    def serialize_curator(self):
        if self.cats:
            cats = [cat.serialize_cat_bis() for cat in self.cats]
        return {
            'name': self.name,
            'legal_number': self.legal_number,
            'phone': self.phone,
            'email': self.email,
            'facebook': self.facebook,
            'cats': [cat.serialize_cat_bis() for cat in self.cats]
        }    
    def serialize_curator_bis(self):
        return {
            'name': self.name,
            'legal_number': self.legal_number,
            'phone': self.phone,
            'email': self.email,
            'facebook': self.facebook
        }