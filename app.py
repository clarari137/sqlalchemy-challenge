# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:////Users/clararichardson/Desktop/RiceDataAnalytics/AnalysisProjects/SQL/Challenge10_SQLAlchemy/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Create necessary variables
year_before = dt.date(2017,8,23) - dt.timedelta(weeks=52)

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
        f"/api/v1.0/precipitation Dictionary including one year of dates and precipitation values <br/>"
        f"/api/v1.0/stations List of stations <br/>"
        f"/api/v1.0/tobs One year of temperature observations for the most active station<br/>"
        f"/api/v1.0/<start> Insert start date YYYY,M,DD<br/> "
        f"/api/v1.0/<start>/<end> Insert start date/end date YYYY,M,DD <br/>"
    )

# Precipitation Observations
@app.route("/api/v1.0/precipitation")
def precip():
    """Return a dictionary of precipitation values"""
    # Using query from climate analysis, select one year of data
    last12 = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date>year_before).all()
    # Convert to dictionary, jsonify
    last12_dict = dict(last12)
    return jsonify(last12_dict)

# Station List
@app.route("/api/v1.0/stations")
def stations():
    # Query all stations and group by to avoid repetition
    station = session.query(measurement.station).group_by(measurement.station).all()
    # Convert to list, jsonify
    station_list = list(np.ravel(station))
    return jsonify(station_list)

# Temperature Observations
@app.route("/api/v1.0/tobs")
def tobs():
    # Query specific station data and create list, jsonify
    station_last12 = session.query(measurement.tobs).\
        filter(measurement.date>=year_before).\
        filter(measurement.station == 'USC00519281').all()
    station_last12_list = list(np.ravel(station_last12))
    return jsonify(station_last12_list)

# Start Date Provided
@app.route("/api/v1.0/<start>")
def start(start):
    # Minimum, maximum, and average temperature observed for provided start date
    start_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
    start_list = list(np.ravel(start_stats))
    return jsonify(start_list)

# Start and End Date Provided
@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    # Minimum, maximum, and average temperature observed for provided start and end date
    startend_stats = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date<=end).all()
    startend_list = list(np.ravel(startend_stats))
    return jsonify(startend_list)

if __name__ == '__main__':
    app.run(debug=True)

session.close()