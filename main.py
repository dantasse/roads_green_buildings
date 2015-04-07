#!/usr/bin/env python

import requests, cStringIO, base64
from flask import Flask, render_template, jsonify
import numpy as np, mahotas as mh, time
import matplotlib.pyplot as plt
app = Flask(__name__)

@app.route("/")
def get_main():
    return render_template('index.html')

# temporary for debugging
def save_to_desktop(image_content):
    outfile = open('/Users/dtasse/Desktop/test.png', 'w')
    outfile.write(image_content)
    outfile.close() 
    
# given a lat/lon pair, saves a satellite image from Google's static maps API.
def get_static_map(lat, lon):
    base_url = "http://maps.google.com/maps/api/staticmap"
    params = {'center': ','.join((str(lat), str(lon))),
        'zoom': 18,
        'size': '640x640',
        'maptype': 'satellite',
        'scale': 2}
    r = requests.get(base_url, params=params)
    save_to_desktop(r.content)
    return r

@app.route("/image_for_map")
def get_image_for_map():
    base_url = "http://maps.google.com/maps/api/staticmap"
    params = {'center': ','.join((str(40.441), str(-80))),
        'zoom': 18,
        'size': '640x640',
        'maptype': 'satellite',
        'scale': 2}
    r = requests.get(base_url, params=params)
    # TODO ok you are returning an image! now mess with it.
    return jsonify({'image': base64.b64encode(r.content)})

if __name__=='__main__':
    # get_static_map(40.441667, -80)
    app.run(debug=True)

