#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import os 
import sys
import datetime
from models import app, db, Venue, Artist, Show

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app.config.from_object('config')
moment = Moment(app)
db.init_app(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  data = []
  venues = Venue.query.all()
  
  for venue in venues:
    data.append({
      "city": venue.city,
      "state": venue.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": db.session.query(Show).filter(venue.id==Show.venue_id).filter(Show.start_time>datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).count()
      }]
      
    })
    
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term=request.form.get('search_term', '')
  data = []
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  
  for venue in venues:
    data.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": db.session.query(Show).join(Venue, venue.id == Show.venue_id ).filter(Show.start_time  > datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).count()
      
    })
    
  response={
    "count": len(venues),
    "data": data
  }
  
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  
  data_list = []
  upcoming_shows = []
  past_shows = []
  
  venues = Venue.query.all() #all venues
  
  for venue in venues:
    
    upcshows =  db.session.query(Show).join(Venue, Venue.id == Show.venue_id ).filter(Show.start_time  > datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).all()
    #all upcoming shows
    
    pstshows = db.session.query(Show).join(Venue, Venue.id == Show.venue_id ).filter(Show.start_time < datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).all()
    #all past shows
    
    for show in upcshows:
      us_artists = db.session.query(Artist).join(Show, Artist.id == show.artist_id ).all()
      #artists in upcoming shows
      
      for artist in us_artists:
        upcoming_shows.append({
          "artist_id" : artist.id,
          "artist_name" : artist.name,
          "artist_image_link" : artist.image_link,
          "start_time": db.session.query(Show.start_time).filter(Show.artist_id == artist.id).first()[0]
        })
      
    for show in pstshows:
      ps_artists = db.session.query(Artist).join(Show, Artist.id == show.artist_id ).all()
      #artists in past shows
      
      for artist in ps_artists:
        past_shows.append({
          "artist_id" : artist.id,
          "artist_name" : artist.name,
          "artist_image_link" : artist.image_link,
          "start_time": db.session.query(Show.start_time).filter(Show.artist_id == artist.id).first()[0]
        })
      
      
    data_list.append({
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.looking_for_talent,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
      })
     # TODO: replace with real venue data from the venues table, using venue_id
  data_list = list(filter(lambda d: d['id'] == venue_id, data_list))[0]
  return render_template('pages/show_venue.html', venue=data_list)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  #fetch data from the form
  name = request.form["name"]
  city = request.form["city"]
  state = request.form["state"]
  address = request.form["address"]
  phone = request.form["phone"]
  genres = request.form["genres"]
  facebook_link = request.form["facebook_link"]
  image_link = request.form["image_link"]
  website_link = request.form["website_link"]
  looking_for_talent = request.form.get("seeking_talent")
  seeking_description = request.form["seeking_description"]
      
  if looking_for_talent != None:
    looking_for_talent = True
  else:
    looking_for_talent = False
  
  data = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, looking_for_talent=looking_for_talent, seeking_description=seeking_description)
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    #save the venue to the database
      db.session.add(data)
      db.session.commit()
      # TODO: insert form data as a new Venue record in the db, instead
      # print("name: "+name+"\ncity: "+city+"\nstate: "+state+"\n address: "+address+"\n phone: "+phone+"\ngenres: "+genres+"\n fb_link: "+facebook_link+"\nimage: "+image_link+website_link+"\ntalent: "+str(looking_for_talent+"\n desc: "+seeking_description)
            
      flash('Venue ' + data.name + ' was successfully listed!')    
      # on successful db insert, flash success  
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # TODO: on unsuccessful db insert, flash an error instead.
    
  finally:
    db.session.close()
 
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  
  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash('The venue was successfully deleted!') 
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong, the venue could not be deleted!') 
  finally:
    db.session.close()
  
  return jsonify({ 'success': True })
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = db.session.query(Artist.id, Artist.name).all()
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term=request.form.get('search_term', '')
  data = []
  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": db.session.query(Show).join(Artist, artist.id == Show.artist_id ).filter(Show.start_time  > datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).count()
      
    })
    
  response={
    "count": len(artists),
    "data": data
  }
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  data_list = []
  upcoming_shows = []
  past_shows = []
  
  artists = Artist.query.all() #all artists
  
  for artist in artists:
     
    upcshows =  db.session.query(Show).join(Artist, artist.id == Show.artist_id ).filter(Show.start_time  > datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).all()
    #all upcoming shows
    
    pstshows = db.session.query(Show).join(Artist, artist.id == Show.artist_id).filter(Show.start_time < datetime.datetime.now().strftime('%Y-%d-%m %H:%M:%S')).all()
    #all past shows
    
    for show in upcshows:
      us_venue = db.session.query(Venue).join(Show, Venue.id == show.venue_id ).all()
      #venue in upcoming shows
      
      for venue in us_venue: 
        upcoming_shows.append({
          "venue_id" : venue.id,
          "venue_name" : venue.name,
          "artist_image_link" : venue.image_link,
          "start_time": db.session.query(Show.start_time).filter(Show.artist_id == venue.id).first()[0]
          })
      
    for show in pstshows:
      ps_venue = db.session.query(Venue).join(Show, Venue.id == show.venue_id ).all()
      #venue in past shows
      
      for venue in ps_venue:
        past_shows.append({
          "venue_id" : venue.id,
          "venue_name" : venue.name,
          "artist_image_link" : venue.image_link,
          "start_time": db.session.query(Show.start_time).filter(Show.artist_id == venue.id).first()[0]
          })
      
      
    
    data_list.append({
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.looking_for_venues,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }
      )
  
  data_list = list(filter(lambda d: d['id'] == artist_id, data_list))[0]
  return render_template('pages/show_artist.html', artist=data_list)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  #get the artist to update from the db
  artist = Artist.query.get(artist_id)
    
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  # called upon submitting the new artist listing form
  name = request.form["name"]
  city = request.form["city"]
  state = request.form["state"]
  phone = request.form["phone"]
  genres = request.form["genres"]
  facebook_link = request.form["facebook_link"]
  image_link = request.form["image_link"]
  website_link = request.form["website_link"]
  looking_for_venues = request.form.get("seeking_venue")
  seeking_description = request.form["seeking_description"]
    
  if looking_for_venues != None:
    looking_for_venues = True
  else:
    looking_for_venues = False
    
  #get the artist to update from the db
  artist = Artist.query.get(artist_id)
  
  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.image_link = image_link
    artist.website_link = website_link
    artist.looking_for_venues = looking_for_venues
    artist.seeking_description = seeking_description
    
    db.session.commit()
    flash('Artist ' + artist.name + ' updated successfully!') 
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong, artist update failed!')  
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
   #fetch data from the updated form
  name = request.form["name"]
  city = request.form["city"]
  state = request.form["state"]
  address = request.form["address"]
  phone = request.form["phone"]
  genres = request.form["genres"]
  facebook_link = request.form["facebook_link"]
  image_link = request.form["image_link"]
  website_link = request.form["website_link"]
  looking_for_talent = request.form.get("seeking_talent")
  seeking_description = request.form["seeking_description"]
      
  if looking_for_talent != None:
    looking_for_talent = True
  else:
    looking_for_talent = False
    
  #get the venue to update from the db
  venue = Venue.query.get(venue_id)
  
  try:
    #update existing venue records
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.image_link = image_link
    venue.website_link = website_link
    venue.looking_for_talent = looking_for_talent
    venue.seeking_description = seeking_description
    
    db.session.commit()
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    flash('Venue ' + venue.name + ' updated successfully!')  
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('Something went wrong, venue update failed!')  
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  
  # called upon submitting the new artist listing form
  name = request.form["name"]
  city = request.form["city"]
  state = request.form["state"]
  phone = request.form["phone"]
  genres = request.form["genres"]
  facebook_link = request.form["facebook_link"]
  image_link = request.form["image_link"]
  website_link = request.form["website_link"]
  looking_for_venues = request.form.get("seeking_venue")
  seeking_description = request.form["seeking_description"]
    
  if looking_for_venues != None:
    looking_for_venues = True
  else:
    looking_for_venues = False
    
      
  data = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, looking_for_venues=looking_for_venues, seeking_description=seeking_description)
  # TODO: modify data to be the data object returned from db insertion
  # print("name: "+name+"\ncity: "+city+"\nstate: "+state+"\n phone: "+phone+"\ngenres: "+genres+"\n fb_link: "+facebook_link+"\nimage: "+image_link+website_link+"\nvenue: "+str(looking_for_venues)+"\n desc: "+seeking_description)
  try:
    db.session.add(data)
    db.session.commit()
     # TODO: insert form data as a new Venue record in the db, instead
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
  finally:
    db.session.close()   
          
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = db.session.query(Venue.id, Venue.name, Artist.id, Artist.name, Artist.image_link, Show.start_time).all()
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
# called to create new shows in the db, upon submitting new show listing form
def create_show_submission():
  artist_id = request.form["artist_id"]
  venue_id = request.form["venue_id"]
  start_time = request.form["start_time"]
  
  show = Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
  print("\nartist: "+artist_id+"\nvenue: "+venue_id+"\ntime: "+start_time)
  try:
    db.session.add(show)
    db.session.commit()
    # TODO: insert form data as a new Show record in the db, instead
    flash('Show was successfully listed!')
    # on successful db insert, flash success
  except :
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
# if __name__ == '__main__':
#     app.run()

# Or specify port manually:

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

