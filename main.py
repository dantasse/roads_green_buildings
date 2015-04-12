#!/usr/bin/env python

import requests, cStringIO, base64, pprint, urllib
from flask import Flask, render_template, jsonify, request
import numpy as np, mahotas as mh, time
import matplotlib.pyplot as plt
from skimage import io
app = Flask(__name__)

# Size of the images we're looking at.
WIDTH = 640
HEIGHT = 640

@app.route("/")
def get_main():
    return render_template('index.html')

# temporary for debugging
def save_to_desktop(image_content, filename):
    outfile = open('/Users/dtasse/Desktop/' + filename, 'w')
    outfile.write(image_content)
    outfile.close()
    
# img is a numpy array representing an image.
def get_percent_red(img):
  # numpy: * is per-item.
  # uses anything where red > 250 b/c I'm not sure why I told it red
  # is #ff0000 but it's giving me red=254.
  n_red = sum(sum((img[:,:,0]>250)*(img[:,:,1] == 0)*(img[:,:,2]==0)))
  return n_red * 1.0 / (WIDTH * HEIGHT)

@app.route("/image_for_map")
def get_image_for_map():
#    static_map_url = "https://maps.google.com/maps/api/staticmap"
#    center_lat = request.args.get('center_lat')
#    center_lng = request.args.get('center_lng')
#    print ','.join((center_lat, center_lng))
#    static_map_params = {'center': ','.join((center_lat, center_lng)),
#        'zoom': int(request.args.get('zoom')),
#        'size': '640x640',
#        'maptype': 'satellite',
#        'scale': 2}
#    static_map_res = requests.get(static_map_url, params=static_map_params)

    osm_url = "http://api.openstreetmap.org/api/0.6/map"
    left = request.args.get('sw_lng')
    bottom = request.args.get('sw_lat')
    right = request.args.get('ne_lng')
    top = request.args.get('ne_lat')
    osm_params = {'bbox': ','.join((left, bottom, right, top))}
    osm_res = requests.get(osm_url, params=osm_params)
    save_to_desktop(osm_res.content, 'osmdata.xml')
    
    roads_url = "https://maps.googleapis.com/maps/api/staticmap"
    center_lat = request.args.get('center_lat')
    center_lng = request.args.get('center_lng')
    roads_params = {'center': ','.join((center_lat, center_lng)),
        'format': 'png',
        'size': 'x'.join([str(WIDTH), str(HEIGHT)]),
        'maptype': 'roadmap',
        'sensor': 'false',
        'zoom': 18,
        'style': ['feature:road|element:labels|visibility:off', 'feature:transit.station|visibility:off', 'element:labels.text|visibility:off', 'feature:poi|visibility:off', 'feature:road|element:geometry.fill|color:0xff0000', 'feature:landscape.man_made|visibility:off', 'feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:8', 'feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:6', 'feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:4']
    }
#    roads_res = requests.get(roads_url, params=roads_params)
    
#    save_to_desktop(roads_res.content, 'roads.png')
    formatted_url = '?'.join([roads_url, urllib.urlencode(roads_params, doseq=True)])
    print formatted_url
    roads_img = io.imread(formatted_url) # reads as a numpy array
    percent_roads = get_percent_red(roads_img)
    print "this percent red: %.04s" % str(percent_roads)
#    save_to_desktop(img, 'roads.png')
    # TODO process this roads image
    
    return jsonify({'osm_content': osm_res.content,
                    'roads_image_url': formatted_url,
                   'pct_roads': percent_roads})
#    return jsonify({'image': base64.b64encode(static_map_res.content),
#                    'osm_content': osm_res.content})

if __name__=='__main__':
    app.run(debug=True)

