#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ARRAY, ForeignKey
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from forms import *
from config import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://postgres:password@localhost:5432/fyyurapp'
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# : connect to a local postgresql database 
migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model): #creates Venue database table 
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref=('Venues'))
    Artist = db.relationship('Artist', secondary='shows')

    # : implement any missing fields, as a database migration using Flask-Migrate
    def to_dict(self):
      return{
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'address': self.address,
        'phone': self.phone,
        'genres': self.genres.split(','),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_talent': self.seeking_talent,
        'seeking_description': self.seeking_description,
      }
      def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
      
      # : implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model): #creates Artist database table
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    Venue = db.relationship('Venue', secondary='shows')
    shows = db.relationship('Show', backref=('Artists'))
    # : implement any missing fields, as a database migration using Flask-Migrate - check
    def to_dict(self):
      return{
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres.split(','),
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website': self.website,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description,
      }

      def __repr__(self):
        return f'<Artist {self.id} {self.name}>' #as shown in lesson

  #  Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model): #creates Show database table 
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  Venue = db.relationship('Venue')
  Artist = db.relationship('Artist')

  def __repr__(self):
    return f'<Show {self.id}'

  #----------------------------------------------------------------------------#
  # Filters.
  #----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  value = str(value) #without this, it gives a parcing error. Parser must be a str or char stream
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

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
def venues(): #displays venues under venue tab
  # : replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue. - check
  # venues = Venue.query.order_by(Venue.state, Venue.city).all()
  # data = db.session.query(Venue).all()
  cities = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []
  for place in cities:
    venue_area = Venue.query.filter_by(state=place.state).filter_by(city=place.city).all()
    data_venue = []
    for venue in venue_area:
      data_venue.append ({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time > datetime.now()).all())
      })
    data.append({
      "city": place.city,
      "state": place.state,
      "venues": data_venue
    })
  return render_template('pages/venues.html', areas=data, venues=venues) #areas=data populates venues underneath their state/city

@app.route('/venues/search', methods=['POST'])
def search_venues(): #ability to search for certain venues
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')
  data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  count = []
  for outcome in data:
    count.append({
      "id":outcome.id,
      "name": outcome.name,
      "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == outcome.id).filter(Show.start_time > datetime.now()).all())
    })
  response = {
    "count":len(data),
    "data": count
  }
    #.ilike is used for pattern matching in PostgreSQL 
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): #shows the venue page 
  # shows the venue page with the given venue_id
  # : replace with real venue data from the venues table, using venue_id
  data = db.session.query(Venue).filter(Venue.id == venue_id).all()
  shows = db.session.query(Show).filter(Show.venue_id == venue_id).all()
  upcoming_shows = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time >= str(datetime.now()).split('.',1)[0]).all()
  previous_showings = db.session.query(Show).filter(Show.venue_id == venue_id).filter(Show.start_time <= str(datetime.now()).split('.',1)[0]).all()

  venues = []
  for showing in shows:
    print(showing.venue_id)
    for upcoming in upcoming_shows:
      upcoming.venue_name=db.session.query(Venue.name).filter_by(id=upcoming.venue_id).first()[0]
      upcoming.venue_image_link=db.session.query(Venue.image_link).filter_by(id=upcoming.venue_id).first()[0]
      upcoming.artist_name=db.session.query(Artist.name).filter_by(id=upcoming.artist_id).first()[0]
      upcoming.artist_image_link=db.session.query(Artist.image_link).filter_by(id=upcoming.artist_id).first()[0]
    for past in previous_showings:
      past.venue_name=db.session.query(Venue.name).filter_by(id=past.venue_id).first()[0]
      past.venue_image_link=db.session.query(Venue.image_link).filter_by(id=past.venue_id).first()[0]
      past.artist_name=db.session.query(Artist.name).filter_by(id=past.artist_id).first()[0]
      past.artist_image_link=db.session.query(Artist.image_link).filter_by(id=past.artist_id).first()[0]
    for info in data:
      info.upcoming_shows=upcoming_shows
      info.previous_showings=previous_showings
      info.upcoming_shows_count=len(upcoming_shows)
      info.previous_showings_count=len(previous_showings)

  return render_template('pages/show_venue.html', venue=data[0])

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): #creates created venue into db 
  # : insert form data as a new Venue record in the db, instead - check
  # : modify data to be the data object returned from db insertion

  form = VenueForm()
  error = False

  try:
    create_venue = Venue()
    create_venue.name = request.form['name']
    create_venue.city = request.form['city']
    create_venue.state = request.form['state']
    create_venue.phone = request.form['phone']
    create_venue.address = request.form['address']
    place_holder_genres = request.form.getlist('genres')
    create_venue.genres = ','.join(place_holder_genres)
    create_venue.facebook_link = request.form['facebook_link']
    db.session.add(create_venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.') #flash an error for unsuccessful db insert
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!') #flash for successful db insert
  # on successful db insert, flash success
  # : on unsuccessful db insert, flash an error instead. - check
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # : Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    # check - learned this from todoapp leason 
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    flash('This venue can not be deleted.') #case where session commit could fail
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for("pages/home.html")) #redirect to homepage
  # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists(): #display artist under artist tab
  # : replace with real data returned from querying the database
  data = db.session.query(Artist).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists(): #search through Artists and get results that match
  # : implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term')
  data = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%'))
  count = []
  for outcome in data:
    count.append(outcome.name)
  response = {
    "count": len(count),
    "data": data,
  }
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id): # shows the venue page with the given venue_id
  # : replace with real venue data from the venues table, using venue_id
  #similar to show_venue 
  data = db.session.query(Artist).filter(Artist.id == artist_id).all()
  shows = db.session.query(Show).filter(Show.artist_id == artist_id).all()
  upcoming_shows = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time >= str(datetime.now()).split('.',1)[0]).all()
  previous_showings = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time <= str(datetime.now()).split('.',1)[0]).all()

  for showing in shows:
    print(showing.venue_id)
    for upcoming in upcoming_shows:
      upcoming.venue_name=db.session.query(Venue.name).filter_by(id=upcoming.venue_id).first()[0]
      upcoming.venue_image_link=db.session.query(Venue.image_link).filter_by(id=upcoming.venue_id).first()[0]
    for past in previous_showings:
      past.venue_name=db.session.query(Venue.name).filter_by(id=past.venue_id).first()[0]
      past.venue_image_link=db.session.query(Venue.image_link).filter_by(id=past.venue_id).first()[0]
    for info in data:
      info.upcoming_shows=upcoming_shows
      info.upcoming_shows_count=len(upcoming_shows)
      info.previous_showings_count=len(previous_showings)
      info.previous_showings=previous_showings

  return render_template('pages/show_artist.html', artist=data[0])

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):# : populate form with fields from artist with ID <artist_id>
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # : take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try: #similar to create 
    edit_artist = Artist.query.get(artist_id) #populate form from artist_id
    edit_artist.name = request.form['name']
    edit_artist.city = request.form['city']
    edit_artist.state = request.form['state']
    edit_artist.phone = request.form['phone']
    place_holder_genres = request.form.getlist('genres')
    edit_artist.genres = ','.join(place_holder_genres)
    edit_artist.facebook_link = request.form['facebook_link']
    db.session.add(edit_artist)
    db.session.commit()
  except: #error case checkings
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      return redirect(url_for("pages/home.html"))
    else:
      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id): #similar to edit artist
  form = VenueForm()
  venue = Venue.query.get(venue_id).to_dict()
  # : populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id): #similar to edit artist submission
  # : take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  edit_venue = Venue.query.get(venue_id)
  error = False
  try: #similar to create 
    edit_venue.name = request.form['name']
    edit_venue.city = request.form['city']
    edit_venue.state = request.form['state']
    edit_venue.address = request.form['address']
    edit_venue.phone = request.form['phone']
    place_holder_genres = request.form.getlist('genres')
    edit_venue.genres = ','.join(place_holder_genres)
    edit_venue.facebook_link = request.form['facebook_link']
    db.session.add(edit_venue)
    db.session.commit()
  except: #error case checkings
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('Looks like there was an error. Form was not updated.')
    else:
      flash('Venue was update!')
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission(): #similar to create venue submission
  # called upon submitting the new artist listing form
  # : insert form data as a new Venue record in the db, instead
  # : modify data to be the data object returned from db insertion

  form = ArtistForm()
  error = False

  try:
    create_artist = Artist()
    create_artist.name = request.form['name']
    create_artist.city = request.form['city']
    create_artist.state = request.form['state']
    create_artist.phone = request.form['phone']
    place_holder_genres = request.form.getlist('genres')
    create_artist.genres = ','.join(place_holder_genres)
    create_artist.facebook_link = request.form['facebook_link']
    db.session.add(create_artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occured. Artist ' + request.form['name'] + ' could not be listed.') #flash an error for unsuccessful db insert
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!') #flash for successful db insert 

  #NOTES FROM PROJECT
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # : replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  show_data = db.session.query(Show).all()
  venue_data = []
  for show in show_data:
    show.venue_name = db.session.query(Venue.name).filter_by(id=show.venue_id).first()[0]
    show.artist_name = db.session.query(Artist.name).filter_by(id=show.artist_id).first()[0]
    show.artist_image_link = db.session.query(Artist.image_link).filter_by(id=show.artist_id).first()[0]
    venue_data.append(show)
  return render_template('pages/shows.html', shows=venue_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # : insert form data as a new Show record in the db, instead
  
  form = ShowForm()
  error = False
  try:
    create_show = Show()
    create_show.artist_id = request.form['artist_id']
    create_show.venue_id = request.form['venue_id']
    create_show.start_time = request.form['start_time']
    db.session.add(create_show)
    db.session.commit()
  except: #error case checkings, similar to before 
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Show could not be listed.')
    else:
      flash('Show was successfully listed!')

  #NOTES FROM PROJECT
  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # : on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

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
