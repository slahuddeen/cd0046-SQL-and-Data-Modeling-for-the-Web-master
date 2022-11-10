# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from os import abort
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
import sys
from models import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#db = SQLAlchemy(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # split area and venue in the db to another table
    areas = Area.query.all()
    data = []
    for area in areas:
        area.venues = Venue.query.filter_by(
            area_id=area.id).order_by('id').all()
        for venue in area.venues:
          venue.num_upcoming_shows = Show.query.filter_by(
            venue_id=venue.id).order_by('id').count()
          
        data.append(area)
    print("done!")
    # join with areas table
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search = request.form.get('search_term', '')
  query = db.session.query(Venue).filter(Venue.name.ilike('%' + search + '%')).all()
  count  = len(query)
  data = []

  for row in query:
    data.append({
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows":1
    })

  response={
    "count": count,
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  result = db.session.query(Venue).filter_by(id=venue_id).first()
  area = Area.query.filter_by(id=result.area_id).first()

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  for show in past_shows_query:
      past_shows.append({
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
  upcoming_shows = []
  for show in upcoming_shows_query:
      upcoming_shows.append({
                  "artist_id": show.artist_id,
                  "artist_name": show.artist.name,
                  "artist_image_link": show.artist.image_link,
                  "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
              })

  data = {
    "id": result.id,
    "name": result.name,
    "genres": result.genres,
    "address": result.address,
    "city": area.city,
    "state": area.state,
    "phone": result.phone,
    "website": result.website,
    "facebook_link": result.facebook_link,
    "seeking_talent": result.seeking_talent,
    "seeking_description": result.seeking_description,
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['GET', 'POST'])
def create_venue_submission():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        address = request.get_json()['address']
        phone = request.get_json()['phone']
        image_link = request.get_json()['image_link']
        facebook_link = request.get_json()['facebook_link']
        genres = request.get_json()['genres']
        seeking_talent = request.get_json()['seeking_talent']
        seeking_description = request.get_json()['seeking_description']

        if seeking_talent == 'y':
            seeking_talent = True
        else:
            seeking_talent =False
        #is the area already in the db, if not then make it.
        area = Area.query.filter_by(city=city, state=state).first()
        if area is None:
          area = Area(
            city=city,
            state=state
          )
          db.session.add(area)
          db.session.commit()

        venue = Venue(
          name=name,
          address=address,
          phone=phone,
          image_link=image_link,
          facebook_link=facebook_link,
          area_id=area.id,
          genres=genres,
          seeking_talent=seeking_talent,
          seeking_description=seeking_description
        )

        db.session.add(venue)
        db.session.commit()

        body['name'] = venue.name
        body['city'] = area.city
        body['state'] = area.state
        body['address'] = venue.address
        body['phone'] = venue.phone
        body['image_link'] = venue.image_link
        body['facebook_link'] = venue.facebook_link

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()

    if error:
        flash('there was an error inserting Venue ' +
              body['name'])
        abort(500)
    else:
        flash('Venue ' + body['name']  + ' was successfully listed!')
        #return render_template('pages/home.html')
        return jsonify(body)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    return jsonify({ 'success': True })

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search = request.form.get('search_term', '')
  query = db.session.query(Artist).filter(Artist.name.ilike('%' + search + '%')).all()
  count  = len(query)
  data = []

  for row in query:
    data.append({
      "id": row.id,
      "name": row.name,
      "num_upcoming_shows":1
    })

    response={
    "count": count,
    "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    
    result = db.session.query(Artist).filter_by(id=artist_id).first()
    area = Area.query.filter_by(id=result.area_id).first()

    past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
    past_shows = []
    for show in past_shows_query:
        past_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "artist_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   
    upcoming_shows = []
    for show in upcoming_shows_query:
        upcoming_shows.append({
                    "venue_id": show.venue_id,
                    "venue_name": show.venue.name,
                    "artist_image_link": show.venue.image_link,
                    "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
                })

    data = {
        "id": result.id,
        "name": result.name,
        "genres": result.genres,
        "city": area.city,
        "state": area.state,
        "phone": result.phone,
        "facebook_link": result.facebook_link,
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    
    error = False
    body={}
    try:
        venue = Venue.query.get(venue_id)
        area = Area.query.get(venue.area_id)
        body['name'] = venue.name
        body['genres'] = venue.genres
        body['address'] = venue.address
        body['city'] = area.city
        body['state'] = area.state
        body['phone'] = venue.phone
        body['website'] = venue.website
        body['facebook_link'] = venue.facebook_link
        body['seeking_talent'] = venue.seeking_talent
        body['seeking_description'] = venue.seeking_description
        body['image_link'] = venue.image_link
    except:
        error = True
        print(sys.exc_info())
    if error:
        abort(500)
    else:
        return render_template('forms/edit_venue.html', form=form, venue=venue, area=area, body=body)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    name = request.get_json()['name']
    genres = request.get_json()['genres']
    address = request.get_json()['address']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    website = request.get_json()['website']
    facebook_link = request.get_json()['facebook_link']
    seeking_talent = request.get_json()['seeking_talent']
    seeking_description = request.get_json()['seeking_description']
    image_link = request.get_json()['image_link']

    if seeking_talent == 'y':
        seeking_talent = True
    else:
        seeking_talent =False

    error= False
    try:
        venue = Venue.query.get(venue_id)
        area = Area.query.get(venue.area_id)

        area = Area.query.filter_by(city=city, state=state).first()
        if area is None:
          area = Area(
            city=city,
            state=state
          )
          db.session.add(area)
          db.session.commit()

        venue.name = name
        venue.genres = genres
        venue.area_id = area.id
        venue.address = address
        venue.phone = phone
        venue.website = website
        venue.facebook_link = facebook_link
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description
        venue.image_link = image_link
          
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    if error:
        abort(500)
    return '', 200

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
    body = {}
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        genres = request.get_json()['genres']
        phone = request.get_json()['phone']
        image_link = request.get_json()['image_link']
        facebook_link = request.get_json()['facebook_link']

        #is the area already in the db, if not then make it.
        area = Area.query.filter_by(city=city, state=state).first()
        if area is None:
          area = Area(
            city=city,
            state=state
          )
          db.session.add(area)
          db.session.commit()

        artist = Artist(
          name=name,
          genres=genres,
          phone=phone,
          image_link=image_link,
          facebook_link=facebook_link,
          area_id=area.id
        )

        db.session.add(artist)
        db.session.commit()
        
        body['name'] = artist.name
        body['city'] = area.city
        body['state'] = area.state
        body['phone'] = artist.phone
        body['image_link'] = artist.image_link
        body['facebook_link'] = artist.facebook_link

    except:
        db.session.rollback()
        error = True
        print(sys.exc_info)
    finally:
        db.session.close()

    if error:
        flash('there was an error inserting Artist ' +
              body['name'] + '!')
        abort(500)
    else:
        flash('Artist ' + body['name']  + ' was successfully listed!')
        #return render_template('pages/home.html')
        return jsonify(body)
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  result = db.session.query(Show).all()
  data = []

  for row in result:
    data.append({
      "venue_id": row.venue_id,
      "venue_name": row.venue.name,
      "artist_id": row.artist_id,
      "artist_name": row.artist.name,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": row.start_time.strftime("%m/%d/%Y, %H:%M:%S")
    })
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  error_message = ""
  try:
    artist_id = request.form.get("artist_id", False)
    venue_id = request.form.get("venue_id", False)
    start_time = request.form.get("start_time", False)

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    # time_exists = db.session.query(Show.id).filter_by(start_time=show.start_time).first() is not None
    artist_exists = db.session.query(Artist.id).filter_by(id=show.artist_id).first() is not None
    venue_exists = db.session.query(Venue.id).filter_by(id=show.venue_id).first() is not None

    if not artist_exists:
      error_message = "Artist ID doesn't exist"
    if not venue_exists:
      error_message = "Venue ID doesn't exist"

    if artist_exists and venue_exists:
      db.session.add(show)
      db.session.commit()  
    else:
      error = True
  
  except:
    db.session.rollback()
    error = True
    print("some db exception")
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash(error_message)
    abort(500)
  else:
    flash('A Show was successfully listed!')
    # on successful db insert, flash success
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.app_context()
    app.debug = True
    app.run(debug=True)
    app.run(host="0.0.0.0", port=3000)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
