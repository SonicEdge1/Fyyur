#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
import dateutil.parser
import babel
import sys
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy.orm import session
from forms import *
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
db.app = app

migrate = Migrate(app, db)

# #----------------------------------------------------------------------------#
# # Models.
# #----------------------------------------------------------------------------#

# class Venue(db.Model):
#     __tablename__ = 'venue'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.ARRAY(db.String))
#     facebook_link = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     website_link = db.Column(db.String(120))
#     seeking_talent = db.Column(db.Boolean)
#     seeking_description = db.Column(db.String(500))
#     shows = db.relationship('Show', backref='venue', lazy=True)


# class Artist(db.Model):
#     __tablename__ = 'artist'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.ARRAY(db.String))
#     facebook_link = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     website_link = db.Column(db.String(120))
#     seeking_venue = db.Column(db.Boolean)
#     seeking_description = db.Column(db.String(500))
#     shows = db.relationship('Show', backref='artist', passive_deletes=True, lazy=True)


# class Show(db.Model):
#     __tablename__ = 'show'
    
#     id = db.Column(db.Integer, primary_key=True)
#     artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
#     venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
#     start_time = db.Column(db.DateTime, nullable=False)

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
  areas = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).order_by('state').all()
  data = []
  for area in areas:
      venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).order_by('name').all()
      venue_data = []
      data.append({
          'city': area.city,
          'state': area.state,
          'venues': venue_data
      })
      for venue in venues:
          shows = Show.query.filter_by(venue_id=venue.id).order_by('id').all()
          venue_data.append({
              'id': venue.id,
              'name': venue.name,
              'num_upcoming_shows': len(shows)  #Why is this here?  Are venues supposed to be sorted by upcoming shows?
          })
  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  term = request.form.get('search_term').lower()
  data = Venue.query.filter(Venue.name.ilike(f'%{term}%')).all()
  count = len(data)
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id, Show.start_time > datetime.utcnow()).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id==venue_id,Show.start_time < datetime.utcnow()).all()
  past_shows_count = len(past_shows)
  show_index = 0
  artist_index = 1
  data_past_shows = []
  data_upcoming_shows = []
  for show in past_shows:
      data_past_shows.append({
          'artist_id': show[show_index].id,
          'artist_name': show[artist_index].name,
          'artist_image_link': show[artist_index].image_link,
          'start_time': show[show_index].start_time.strftime('%Y-%m-%d %H:%M:%S')
        }) 

  for show in upcoming_shows:
      data_upcoming_shows.append({
          'artist_id': show[show_index].id,
          'artist_name': show[artist_index].name,
          'artist_image_link': show[artist_index].image_link,
          'start_time': show[show_index].start_time.strftime('%Y-%m-%d %H:%M:%S')
        }) 

  data = {
    "name": venue.name,
    "id": venue.id,
    "genres": venue.genres,
    "city": venue.city,
    "address": venue.address,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    'past_shows': data_past_shows,
    'upcoming_shows': data_upcoming_shows,
    'past_shows_count': past_shows_count,
    'upcoming_shows_count': upcoming_shows_count
  }
  # There has got to be a less verbose way to do this...
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    form= VenueForm(request.form)
    newVenue = Venue(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(newVenue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name']  + ' was successfully listed!')
  else:
    flash('Something went wrong listing Venue: ' + request.form['name'] + ' Try again later.')
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = request.form.get('search_term').lower()
  data = Artist.query.filter(Artist.name.ilike(f'%{term}%')).all()
  count = len(data)
  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.get(artist_id)
  now = datetime.utcnow()
  upcoming_shows = db.session.query(Show, Venue).join(Artist, artist_id == Show.artist_id).filter(
    Show.venue_id == Venue.id,
    Show.artist_id == artist_id,
    Show.start_time > now).all()
  upcoming_shows_count = len(upcoming_shows)
  past_shows = db.session.query(Show, Venue).join(Artist, artist_id == Show.artist_id).join(Venue, Show.venue_id == Venue.id).filter(
        Show.venue_id == Venue.id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()).all()
  past_shows_count = len(past_shows)
  upcoming_show_data = []
  past_show_data = []
  show_index = 0
  venue_index = 1
  for show in upcoming_shows:
    upcoming_show_data.append({
      'venue_id': show[venue_index].id,
      'venue_name': show[venue_index].name,
      'venue_image_link': show[venue_index].image_link,
      'start_time': show[show_index].start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  for show in past_shows:
    past_show_data.append({
      'venue_id': show[venue_index].id,
      'venue_name': show[venue_index].name,
      'venue_image_link': show[venue_index].image_link,
      'start_time': show[show_index].start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

  data = {
  "id": artist.id,
  "name": artist.name,
  "genres": artist.genres,
  "city": artist.city,
  "state": artist.state,
  "phone": artist.phone,
  "website": artist.website_link,
  "facebook_link": artist.facebook_link,
  "seeking_venue": artist.seeking_venue,
  "seeking_description": artist.seeking_description,
  "image_link": artist.image_link,
  'past_shows': past_show_data,
  'upcoming_shows': upcoming_show_data,
  'past_shows_count': past_shows_count,
  'upcoming_shows_count': upcoming_shows_count
  }

  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    form=ArtistForm(request.form)

    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    gd = []
    for genre in form.genres.data:
      gd.append(genre)
    artist.genres = gd #form.genres.data,# this would put an array inside an array
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    print("artist.seeking_venue: ", artist.seeking_venue)
    artist.seeking_venue = form.seeking_venue.data
    print("artist.seeking_venue: ", artist.seeking_venue)
    print("form_seeking_venue.data: ", form.seeking_venue.data, " type: ", type(form.seeking_venue.data) )
    artist.seeking_description = form.seeking_description.data
    # db.session.add(artist)
    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully edited!')
  else:
    flash('Something went wrong editing Artist: ' + request.form['name'] + ' Try again later.')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    form= VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name']  + ' was successfully edited!')
  else:
    flash('Something went wrong editing Venue: ' + request.form['name'] + ' Try again later.')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    form=ArtistForm(request.form)
    newArtist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.city.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(newArtist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('Something went wrong listing Artist: ' + request.form['name'] + ' Try again later.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data = []
  try:
    all_shows = db.session.query(Show).all()
    for show in all_shows:
      artist = Artist.query.filter_by(id=show.artist_id).first()
      venue = Venue.query.filter_by(id=show.venue_id).first()
      data.append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "artist_id": show.artist_id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime("%d/%m/%Y, %H:%M")
      })
  except Exception as e:
      print(e)
  return render_template("pages/shows.html", shows=data)



@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    form = ShowForm(request.form)
    newShow = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(newShow)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
  # on successful db insert, flash success
    flash('Show was successfully listed!')
  else:
    flash('Something went wrong listing the show on : ' + request.form['start_time'] + ' Try again later.')
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
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
