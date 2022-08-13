#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from http.client import responses
import re
import sys
import time
from urllib import response
from dateutil.parser import parse
# from dateutil.tz import gettz
import json
import datetime
from dateutil import parser
from datetime import date as dt
import babel
from pip import List
from flask import (Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for, 
    jsonify)
from flask_cors import CORS
from flask_api import status
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import pytz

utc=pytz.UTC
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}}, withCredentials=True, supports_credentials=True)

# TODO: connect to a local postgresql database
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

   

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(500), nullable=True)

    shows = db.relationship('Show', backref='artist', lazy=True)


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime())
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = parser.parse(value)
    print("The Date value = {}".format(date))
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

# CORS Headers 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response


@app.route('/api/')
# @cross_origin()
def index():
    return jsonify({"Message": "Please refer to the documentation for more information"}), 101


#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

@app.route('/api/venues', methods=['GET', 'POST'])
# @cross_origin()
def venues():
    # TODO: replace with real venues data.

    if request.method == 'GET':
        if request.args.get('search') == None:
            local_ = Venue.query.all()

        else:
            word = request.args.get('search')
            keyword = "%{}%".format(word)
            local_ = Venue.query.filter(or_(Venue.id == word, Venue.name.ilike(keyword), Venue.city.ilike(keyword), Venue.state.ilike(keyword), func.concat(Venue.city + ", ", Venue.state).ilike(keyword))).all()

        data = [] 
        for i in range(len(local_)):
            past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == local_[i].id).all()
            upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == local_[i].id).all()
            data = {local_venue.id :{
                'id': local_venue.id,
                'name': local_venue.name,
                'address': local_venue.address,
                'city': local_venue.city,
                'state': local_venue.state,
                'phone': local_venue.phone,
                'genres': local_venue.genres,
                'website': local_venue.website,
                'facebook_link': local_venue.facebook_link,
                'seeking_talent': local_venue.seeking_talent,
                'image_link': local_venue.image_link,
                'past_shows': [{
                'artist_id': p.artist_id,
                'artist_name': p.artist.name,
                'artist_image_link': p.artist.image_link,
                'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
                } for p in past_shows],
                'upcoming_shows': [{
                    'artist_id': u.artist.id,
                    'artist_name': u.artist.name,
                    'artist_image_link': u.artist.image_link,
                    'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
                } for u in upcoming_shows],
                'past_shows_count': len(past_shows),
                'upcoming_shows_count': len(upcoming_shows)
            } for local_venue in local_}

            if local_[i].seeking_talent==True:
                data[local_[i].id]['seeking description'] =  local_[i].seeking_description

        return jsonify(data), 200

    elif request.method == 'POST':
        try:  
            venue = Venue(
                name =request.args.get('name'),
                city =request.args.get('city'),
                state =request.args.get('state'),
                address =request.args.get('address'),
                phone =request.args.get('phone'),
                genres =request.args.getlist('genres'),
                facebook_link =request.args.get('facebook_link'),
                website =request.args.get('website_link'),
                image_link =request.args.get('image_link'),
                seeking_talent =request.args.get('seeking_talent') == 'true',
                seeking_description =request.args.get('seeking_description')
            )
            db.session.add(venue)
            db.session.commit()
            return jsonify({"Success": True, "Message": "Venue " + request.args.get('name') + " was successfully listed!"}), 201
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()
    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405


@app.route('/api/venues/<int:venue_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
# @cross_origin()
def show_venue(venue_id):
    # TODO: replace with real venue data from the venues table, using venue_id
    if request.method == 'GET':
        local_venue = Venue.query.get(venue_id)
        past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.venue_id == local_venue.id).all()
        upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.venue_id == local_venue.id).all()
        data = {
            'id': local_venue.id,
            'name': local_venue.name,
            'address': local_venue.address,
            'city': local_venue.city,
            'state': local_venue.state,
            'phone': local_venue.phone,
            'genres': local_venue.genres,
            'website': local_venue.website,
            'facebook_link': local_venue.facebook_link,
            'seeking_talent': local_venue.seeking_talent,
            'image_link': local_venue.image_link,
            'past_shows': [{
            'artist_id': p.artist_id,
            'artist_name': p.artist.name,
            'artist_image_link': p.artist.image_link,
            'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
            } for p in past_shows],
            'upcoming_shows': [{
                'artist_id': u.artist.id,
                'artist_name': u.artist.name,
                'artist_image_link': u.artist.image_link,
                'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
            } for u in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
        if local_venue.seeking_talent==True:
            data['seeking description'] =  local_venue.seeking_description

        return jsonify(data), 200

    elif request.method == 'DELETE':
        try:
            Show.query.filter_by(venue_id=venue_id).delete()
            Venue.query.filter_by(id=venue_id).delete()
            db.session.commit()
            return jsonify({"Success": True, "Message": "Venue has been successfully deleted!"}), 202
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    elif request.method == 'PUT' or request.method == 'PATCH':
        try:
            venue = Venue.query.filter_by(id=venue_id).all()[0]
            if request.args.get('name') != None: venue.name=request.args.get('name')
            if request.args.get('city') != None: venue.city=request.args.get('city')
            if request.args.get('state') != None: venue.state=request.args.get('state')
            if request.args.get('address') != None: venue.address=request.args.get('address')
            if request.args.get('phone') != None: venue.phone=request.args.get('phone')
            if request.args.getlist('genres') != None: venue.genres=request.args.getlist('genres')
            if request.args.get('facebook_link') != None: venue.facebook_link=request.args.get('facebook_link')
            if request.args.get('website_link') != None: venue.website=request.args.get('website_link')
            if request.args.get('image_link') != None: venue.image_link=request.args.get('image_link')
            if request.args.get('seeking_talent') != None: venue.seeking_talent=request.args.get('seeking_talent') == 'True'
            if request.args.get('seeking_description') != None: venue.seeking_description=request.args.get('seeking_description')

            db.session.commit()
            return jsonify({"Success": True, "Message": "Venue " + request.args.get('name') + " has been updated successfuly"}), 202
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405

    

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------


@app.route('/api/artists', methods=['POST', 'GET'])
# @cross_origin()
def artists():
    # TODO: replace with real data returned from querying the database
    if request.method == 'GET':
        if request.args.get('search') ==  None:
            local_ = Artist.query.all()

        else:
            word = request.args.get('search')
            keyword = "%{}%".format(word)    
            local_ = Artist.query.filter(or_(Artist.id == word, Artist.name.ilike(keyword), Artist.city.ilike(keyword), Artist.state.ilike(keyword), func.concat(Artist.city + ", ", Artist.state).ilike(keyword))).all()
            
        data = []
        print(len(local_))
        for i in range(len(local_)):
            past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == local_[i].id).all()
            upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == local_[i].id).all()
            data = {local_artist.id : {
                'id': local_artist.id,
                'name': local_artist.name,
                'city': local_artist.city,
                'state': local_artist.state,
                'phone': local_artist.phone,
                'genres': local_artist.genres,
                'website': local_artist.website,
                'facebook_link': local_artist.facebook_link,
                'seeking_venue': local_artist.seeking_venue,
                'image_link': local_artist.image_link,
                'past_shows': [{
                    'venue_id': p.venue_id,
                    'venue_name': p.venue.name,
                    'venue_image_link': p.venue.image_link,
                    'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
                    } for p in past_shows],
                'upcoming_shows': [{
                    'venue_id': u.venue.id,
                    'venue_name': u.venue.name,
                    'venue_image_link': u.venue.image_link,
                    'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
                } for u in upcoming_shows],
                'past_shows_count': len(past_shows),
                'upcoming_shows_count': len(upcoming_shows)
            } for local_artist in local_}

            if local_[i].seeking_venue==True:
                data[local_[i].id]['seeking description'] =  local_[i].seeking_description


        return jsonify(data), 200

    elif request.method == 'POST':
        try: 
            artist = Artist(
                name =request.args.get('name'),
                city =request.args.get('city'),
                state =request.args.get('state'),
                phone =request.args.get('phone'),
                genres =request.args.getlist('genres'),
                facebook_link =request.args.get('facebook_link'),
                website =request.args.get('website_link'),
                image_link =request.args.get('image_link'),
                seeking_venue = request.args.get('seeking_venue') == 'True',
                seeking_description =request.args.get('seeking_description')
            )
            db.session.add(artist)
            db.session.commit()
            return jsonify({"Success": True, "Message": "Artist " + request.args.get('name') + " has been successfuly listed!"}), 201
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405


@app.route('/api/artists/<int:artist_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
# @cross_origin()
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    if request.method == 'GET':
        local_artist = Artist.query.get(artist_id)
        past_shows = Show.query.filter(Show.start_time < datetime.now(), Show.artist_id == local_artist.id).all()
        upcoming_shows = Show.query.filter(Show.start_time > datetime.now(), Show.artist_id == local_artist.id).all()
        data = {
            'id': local_artist.id,
            'name': local_artist.name,
            'city': local_artist.city,
            'state': local_artist.state,
            'phone': local_artist.phone,
            'genres': local_artist.genres,
            'website': local_artist.website,
            'facebook_link': local_artist.facebook_link,
            'seeking_venue': local_artist.seeking_venue,
            'image_link': local_artist.image_link,
            'past_shows': [{
                'venue_id': p.venue_id,
                'venue_name': p.venue.name,
                'venue_image_link': p.venue.image_link,
                'start_time': p.start_time.strftime("%m/%d/%Y, %H:%M")
                } for p in past_shows],
            'upcoming_shows': [{
                'venue_id': u.venue.id,
                'venue_name': u.venue.name,
                'venue_image_link': u.venue.image_link,
                'start_time': u.start_time.strftime("%m/%d/%Y, %H:%M")
            } for u in upcoming_shows],
            'past_shows_count': len(past_shows),
            'upcoming_shows_count': len(upcoming_shows)
        }
        if local_artist.seeking_venue==True:
            data['seeking description'] =  local_artist.seeking_description

        return jsonify(data), 200

    elif request.method == 'PATCH' or request.method == 'PUT':
        try:
            artist = Artist.query.filter_by(id=artist_id).all()[0]
            artist.name=request.args.get('name')
            artist.city=request.args.get('city')
            artist.state=request.args.get('state')
            artist.phone=request.args.get('phone')
            artist.genres=request.args.getlist('genres')
            artist.facebook_link=request.args.get('facebook_link')
            artist.website=request.args.get('website_link')
            artist.image_link=request.args.get('image_link')
            artist.seeking_venue=request.args.get('seeking_venue') == 'True'
            artist.seeking_description=request.args.get('seeking_description')
            db.session.add(artist)
            db.session.commit()
            return jsonify({"Success": True, "Message": "Artist has been updated successfully!"}), 202
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    elif request.method == 'DELETE':
        try:
            Show.query.filter_by(artist_id=artist_id).delete()
            Artist.query.filter_by(id=artist_id).delete()
            db.session.commit()
            return jsonify({"Success": True, "Message": "Artist has been successfully deleted!"}), 202
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

@app.route('/api/shows', methods=['GET', 'POST'])
# @cross_origin()
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    if request.method == 'GET':
        if request.args.get('search') ==  None:
            local_shows = Show.query.all()
        else:
            word = request.args.get('search')
            keyword = "{}".format(word)    
            local_shows = Show.query.filter(or_(Show.id == keyword, Show.artist_id == keyword, Show.venue_id == keyword)).all()

        raw = None
        for i in range(len(local_shows)): 
            raw = {s.id : {
                "venue_id": s.venue_id,
                "venue_name": Venue.query.get(s.venue_id).name,
                "artist_id": s.artist_id,
                "artist_name": Artist.query.get(s.artist_id).name,
                "artist_image_link": Artist.query.get(s.artist_id).image_link,
                "start_time": s.start_time.strftime("%m/%d/%Y, %H:%M")
            } for s in local_shows}

        if raw is None:
            data = None
        else:
            data = raw

        return jsonify(data), 200
    
    elif request.method == 'POST':
        try:
            artist_check = Artist.query.get(request.form['artist_id'])
            venue_check = Venue.query.get(request.form['venue_id'])
            if((artist_check != None) and (venue_check != None)):
                show = Show(
                    start_time =request.args.get('start_time'),
                    artist_id =request.args.get('artist_id'),
                    venue_id =request.args.get('venue_id')
                )
                db.session.add(show)
                db.session.commit()
                return jsonify({"Success": True, "Message": "Show " + request.args.get('name') + " has been successfuly listed!"}), 201
            else:
                raise Exception
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405


@app.route('/api/shows/<int:show_id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
# @cross_origin()
def show_(show_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    if request.method == 'GET':
        local_show = Show.query.get(show_id)
        data = {
            "venue_id": local_show.venue_id,
            "venue_name": Venue.query.get(local_show.venue_id).name,
            "artist_id": local_show.artist_id,
            "artist_name": Artist.query.get(local_show.artist_id).name,
            "artist_image_link": Artist.query.get(local_show.artist_id).image_link,
            "start_time": local_show.start_time.strftime("%m/%d/%Y, %H:%M")
        }
        return jsonify(data), 200

    elif request.method == 'PATCH' or request.method == 'PUT':
        try:
            artist_check = Artist.query.get(request.form['artist_id'])
            venue_check = Venue.query.get(request.form['venue_id'])
            if((artist_check != None) and (venue_check != None)):
                show = Show.query.get(show_id)
                show.start_time =request.args.get('start_time')
                show.artist_id =request.args.get('artist_id')
                show.venue_id =request.args.get('venue_id')
                db.session.add(show)
                db.session.commit()
                return jsonify({"Success": True, "Message": "Show has been successfuly listed!"}), 202
            else:
                raise Exception
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    elif request.method == 'DELETE':
        try:
            Show.query.filter_by(id=show_id).delete()
            db.session.commit()
            return jsonify({"Success": True, "Message": "Show has been successfully deleted!"}), 202
        except:
            db.session.rollback()
            return jsonify({"Success": False, "Message": sys.exc_info()}), 400
        finally:
            db.session.close()

    else:
        return jsonify({"Success": False, "Message": sys.exc_info()}), 405



@app.errorhandler(404)
# @cross_origin()
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
# @cross_origin()
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
