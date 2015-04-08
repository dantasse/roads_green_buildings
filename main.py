#!/usr/bin/env python

import requests, cStringIO, base64
from flask import Flask, render_template, jsonify, request
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

@app.route("/image_for_map")
def get_image_for_map():
    static_map_url = "https://maps.google.com/maps/api/staticmap"
    center_lat = request.args.get('center_lat')
    center_lng = request.args.get('center_lng')
    print ','.join((center_lat, center_lng))
    static_map_params = {'center': ','.join((center_lat, center_lng)),
        'zoom': int(request.args.get('zoom')),
        'size': '640x640',
        'maptype': 'satellite',
        'scale': 2}
    static_map_res = requests.get(static_map_url, params=static_map_params)

    osm_url = "http://api.openstreetmap.org/api/0.6/map"
    left = request.args.get('sw_lng')
    bottom = request.args.get('sw_lat')
    right = request.args.get('ne_lng')
    top = request.args.get('ne_lat')
    osm_params = {'bbox': ','.join((left, bottom, right, top))}
    osm_res = requests.get(osm_url, params=osm_params)
    
    return jsonify({'image': base64.b64encode(static_map_res.content),
                    'osm_content': osm_res.content})

if __name__=='__main__':
    app.run(debug=True)

