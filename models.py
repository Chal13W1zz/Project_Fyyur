from flask import Flask
from flask_sqlalchemy import SQLAlchemy

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

db = SQLAlchemy()

# DONE: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    looking_for_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show',backref='Venue',lazy=True)
       
    def __repr__(self):
      return f'<Venue ID: {self.id}, Name: {self.name}, City: {self.city}, State: {self.state}, Address: {self.address}, Phone: {self.phone}, Genres: {self.genres}, FB: {self.facebook_link}, IMG: {self.image_link}, Web: {self.website_link}, TSeek: {self.looking_for_talent}, Desc: {self.seeking_description} >'
    
    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    looking_for_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show',backref='Artist',lazy=True)
    
    def __repr__(self):
      return f'<Artist ID: {self.id}, Name: {self.name}, City: {self.city}, State: {self.state}, Address: {self.address}, Phone: {self.phone}, Genres: {self.genres}, FB: {self.facebook_link}, IMG: {self.image_link}, Web: {self.website_link}, TSeek: {self.looking_for_venues}, Desc: {self.seeking_description} >'
    
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    
class Show(db.Model):
  __tablename__ = "Show"
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.String(), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.