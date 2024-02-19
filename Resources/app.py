# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import os

#################################################
# Database Setup
#################################################

# Get the absolute path to the SQLite database file
db_file_path = os.path.join(os.path.dirname(__file__), 'Resources', 'hawaii.sqlite')

# Create the SQLAlchemy engine
engine = create_engine(f"sqlite:///{db_file_path}")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Connect to the engine
    session = Session(engine)

    # Return a list of all precipitation and date
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert list of tuples into dictionary
    precepitations = []
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
        precepitations.append(precipitation_dict)

    return jsonify(precepitations)

@app.route("/api/v1.0/stations")
def stations():
    # Connect to the engine
    session = Session(engine)

    # Return a list of all stations
    stations = session.query(Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()
    
    session.close()

    all_stations=[]
    for id, station, name, latitude, longitude, elevation in stations:
        station_dict = {}
        station_dict['Id'] = id
        station_dict['station'] = station
        station_dict['name'] = name
        station_dict['latitude'] = latitude
        station_dict['longitude'] = longitude
        station_dict['elevation'] = elevation
        all_stations.append(station_dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tempartureobs():

    session = Session(engine)

    # Return a list of all temparture observation
    dates = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    string_date = list(np.ravel(dates))[0]
    latest_date = dt.datetime.strptime(string_date,"%Y-%m-%d")
    one_year_ago = latest_date-dt.timedelta(days=366)

# Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.tobs).order_by(Measurement.date.desc()).\
            filter(Measurement.date>=one_year_ago).all()
    
    session.close()

# List of temperatures
    temperatures = []
    for tobs,date in results:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        temperatures.append(tobs_dict)
    return jsonify(temperatures)

# Return the minimum, maximum, and average temperatures 
@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Filter the results for the selected date range (between start and end)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()

    temp_obs = {}
    temp_obs["Minimum_Temp"] = results[0][0]
    temp_obs["Average_Temp"] = results[0][1]
    temp_obs["Maximum_Temp"] = results[0][2]
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    
    session = Session(engine)
  
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()
    temp_obs = {}
    temp_obs["Minimum_Temp"] = results[0][0]
    temp_obs["Average_Temp"] = results[0][1]
    temp_obs["Maximum_Temp"] = results[0][2]
    return jsonify(temp_obs)

if __name__ == '__main__':
    app.run(debug=True) 