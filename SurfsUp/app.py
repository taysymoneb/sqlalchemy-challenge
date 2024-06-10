# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

app = Flask(__name__)

#connect to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)


# Save references to each table
measurement = base.classes.measurement
Station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#home route
@app.route("/")
def home():
   return(
      f"<center><h2>Welcome to the Hawaii Climate Analysis Local API!</h2></center>"
      f"<center><h3>Select from one of the available routes: </h3></center>"
      f"<center>/api/v1.0/precipitation</center>"
      f"<center>/api/v1.0/stations</center>"
      f"<center>/api/v1.0/tobs</center>"
      f"<center>/api/v1.0/start/end</center>"
      )

#precipitation route
@app.route("/api/v1.0/precipitation")
def precip():
    #return previous year's precipitation as a json
    #Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date>= previousYear).all()

    session.close()
    #dictionary with the date as key, precip as value
    precipitation = {date: prcp for date, prcp in results}
    #jsonify 
    return jsonify(precipitation)

#station route
@app.route("/api/v1.0/stations")
def stations():
   #show station list
    results = session.query(Station.station).all()
    session.close()

    stationList = list(np.ravel(results))

    return jsonify(stationList) 

#tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    #return the previous year temps
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temps from the most active station from past year
    results = session.query(measurement.date, measurement.tobs).\
            filter(measurement.station == 'USC00519281').\
            filter(measurement.date >= previousYear).all()
    
    session.close()

    tempList = list(np.ravel(results))
    
    #return temp list
    return jsonify(tempList)

#start, end route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    #select statement
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    
    if not end:

        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(measurement.date >= startDate).all()

        session.close()

        tempList = list(np.ravel(results))
    
    #return temp list
        return jsonify(tempList)
    
    else:

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
        .filter(measurement.date >= startDate)\
        .filter(measurement.date <= endDate).all()
        
        session.close()

        tempList = list(np.ravel(results))
    
    #return temp list
        return jsonify(tempList)

## app launcher
if __name__ == '__main__':
   app.run(debug=True)

