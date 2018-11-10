from flask import Flask, render_template, request, send_file
from werkzeug import secure_filename
import pandas
import geopy
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut

geolocator = Nominatim(user_agent="my-application")

def do_geocode(address):
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        return do_geocode(address)

app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success", methods=['POST'])
def success():
    global file
    global df
    try:
        if request.method=='POST':
            file=request.files["file"]
            file.save(secure_filename("uploaded"+file.filename))
            df = pandas.read_csv("uploaded"+file.filename)
            #df = df.iloc[1:5,2:]
            if ("Address" in df.columns) or ("address" in df.columns):
                df["city_coord"] = df["address"].apply(do_geocode)
                df['latitude'] = df['city_coord'].apply(lambda x: x.latitude if x != None else None )
                df['longitude'] = df['city_coord'].apply(lambda x: x.longitude if x != None else None)
                df = df.drop(columns="city_coord")
                df.to_csv("uploaded"+file.filename)
                return render_template("index.html", btn="download.html", data=df.to_html())
            else:
                return render_template("index.html", text="No column with header address or Address present")
    except Exception as e:
        return render_template("index.html", text=str(e))


@app.route("/download")
def download():
    return send_file("uploaded"+file.filename, attachment_filename="yourfile.csv", as_attachment=True)


if __name__ == '__main__':
    app.debug=True
    app.run()