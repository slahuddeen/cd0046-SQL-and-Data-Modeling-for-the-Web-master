
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Area(db.Model):
    __tablename__ = 'area'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    venues = db.relationship('Venue', backref='list', lazy=True)
    artists = db.relationship('Artist', backref='list', lazy=True)

    def __repr__(self):
        return f'<Area ID: {self.id}, city: {self.city}, state: {self.state}, venues: {self.venues}>'

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    num_upcoming_shows = db.Column(db.Integer)
    seeking_talent = db.Column(db.Boolean)
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    shows = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}, address: {self.address}, phone: {self.phone}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, area_id: {self.area_id}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}, phone: {self.phone}, genres: {self.genres}, image_link: {self.image_link}, facebook_link: {self.facebook_link}, area_id: {self.area_id}>'


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    venue_id = db.Column(db.Integer, db.ForeignKey(
            'venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
            'artist.id'), nullable=False)
    start_time =  db.Column(db.DateTime)
