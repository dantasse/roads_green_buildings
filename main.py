#!/usr/bin/env python

import requests, cStringIO, base64, pprint, urllib, time, json
from flask import Flask, render_template, jsonify, request
import numpy as np, mahotas as mh
from skimage import io
import skimage.color

app = Flask(__name__)

# Size of the images we're looking at.
WIDTH = 640
HEIGHT = 640

@app.route("/")
def get_main():
    return render_template('index.html')

# img is a numpy array, WIDTH x HEIGHT x 3 (rgb).
# Returns an img w/ red roads, transparent elsewhere.
def get_roads_image(img):
    roads_pixels = (img[:,:,0] > 250)
    alpha = np.ones(img.shape[0:2]).astype('uint8') * 255
    img = np.dstack((img[:,:,0], img[:,:,1], img[:,:,2], alpha))
    img[-roads_pixels] = [0,0,0,0]
    img[roads_pixels] = [228, 26, 28, 255]
    return img

# img is a numpy array, WIDTH x HEIGHT x 3 (rgb).
def get_percent_red(img):
    # numpy: * is per-item.
    # uses anything where red > 250 b/c I'm not sure why I told it red
    # is #ff0000 but it's giving me red=254.
    n_red = sum(sum((img[:,:,0]>250)*(img[:,:,1] == 0)*(img[:,:,2]==0)))
    return n_red * 1.0 / (WIDTH * HEIGHT)

# returns true iff this point is a building color
def is_bldg(p):
  goodpts = ([242, 240, 233], [242, 238, 226], [244, 242, 234],
            [210, 210, 217], [248, 248, 240], [217, 217, 217],
            [203, 202, 213])
  return np.any([np.all(p == goodpt) for goodpt in goodpts])
  
def get_percent_building(img):
    # 242 240 233 is the interior building RGB.
    # 242 238 226 is close too.
    # 233 229 220 is background.
    # other roofs: (244, 242, 234), (210 210 217), (248 248 240), (217 217 217), (203 202 213)
    
    # TODO ugh all this whole dang function.
    bldg = (img[:,:,0]==242) * (img[:,:,1]==240) * (img[:,:,2]==233)
    bldg2 = (img[:,:,0]==242) * (img[:,:,1]==238) * (img[:,:,2]==226)
    bldg3 = (img[:,:,0]==244) * (img[:,:,1]==242) * (img[:,:,2]==234)
    bldg4 = (img[:,:,0]==210) * (img[:,:,1]==210) * (img[:,:,2]==217)
    bldg5 = (img[:,:,0]==248) * (img[:,:,1]==248) * (img[:,:,2]==240)
    bldg6 = (img[:,:,0]==217) * (img[:,:,1]==217) * (img[:,:,2]==217)
    bldg7 = (img[:,:,0]==203) * (img[:,:,1]==202) * (img[:,:,2]==213)
    bldg8 = (img[:,:,0]==242) * (img[:,:,1]==242) * (img[:,:,2]==234)
    bldg9 = (img[:,:,0]==255) * (img[:,:,1]==255) * (img[:,:,2]==255)
    bldg10 = (img[:,:,0]==251) * (img[:,:,1]==247) * (img[:,:,2]==242)
    bldg11 = (img[:,:,0]==210) * (img[:,:,1]==207) * (img[:,:,2]==217)
    return sum(sum((bldg + bldg2 + bldg3 + bldg4 + bldg5 + bldg6 + bldg7 + bldg8 + bldg9 + bldg10 + bldg11))) * 1.0 / (WIDTH * HEIGHT)

def get_building_image(img):
    bldg = (img[:,:,0]==242) * (img[:,:,1]==240) * (img[:,:,2]==233)
    bldg2 = (img[:,:,0]==242) * (img[:,:,1]==238) * (img[:,:,2]==226)
    bldg3 = (img[:,:,0]==244) * (img[:,:,1]==242) * (img[:,:,2]==234)
    bldg4 = (img[:,:,0]==210) * (img[:,:,1]==210) * (img[:,:,2]==217)
    bldg5 = (img[:,:,0]==248) * (img[:,:,1]==248) * (img[:,:,2]==240)
    bldg6 = (img[:,:,0]==217) * (img[:,:,1]==217) * (img[:,:,2]==217)
    bldg7 = (img[:,:,0]==203) * (img[:,:,1]==202) * (img[:,:,2]==213)
    bldg8 = (img[:,:,0]==242) * (img[:,:,1]==242) * (img[:,:,2]==234)
    bldg9 = (img[:,:,0]==255) * (img[:,:,1]==255) * (img[:,:,2]==255)
    bldg10 = (img[:,:,0]==251) * (img[:,:,1]==247) * (img[:,:,2]==242)
    bldg11 = (img[:,:,0]==210) * (img[:,:,1]==207) * (img[:,:,2]==217)
    # TODO also ugh.
    bldg_pixels = bldg + bldg2 + bldg3 + bldg4 + bldg5 + bldg6 + bldg7 + bldg8 + bldg9 + bldg10 + bldg11
    bldg_pixels = mh.gaussian_filter(bldg_pixels, 2) > .5
    alpha = np.ones(img.shape[0:2]).astype('uint8') * 255
    img = np.dstack((img[:,:,0], img[:,:,1], img[:,:,2], alpha))
    img[-bldg_pixels] = [0,0,0,0]
    img[bldg_pixels] = [55, 126, 184, 255]
    return img
  
# img is a numpy array, WIDTH x HEIGHT x 3 (rgb).
# Returns the number of pixels that are _some kind of_ green. A little
# inexact because who knows exactly what green color you've got.
def get_percent_green(img):
    imghsv = skimage.color.rgb2hsv(img)
    greenpixels = (imghsv[:,:,0] > .2) * (imghsv[:,:,0] < .7) * (imghsv[:,:,1] > .18)
    greenpixels = mh.gaussian_filter(greenpixels, 2) > .5
    return sum(sum(greenpixels)) * 1.0 / (640*640)

def get_green_image(img):
    imghsv = skimage.color.rgb2hsv(img)
    greenpixels = (imghsv[:,:,0] > .2) * (imghsv[:,:,0] < .7) * (imghsv[:,:,1] > .18)
    greenpixels = mh.gaussian_filter(greenpixels, 2) > .5
    alpha = np.ones(img.shape[0:2]).astype('uint8') * 255
    img = np.dstack((img[:,:,0], img[:,:,1], img[:,:,2], alpha))
    img[-greenpixels] = [255,255,255,0]
    return img
  
@app.route("/image_for_map")
def get_image_for_map():

    # FIND ROADS
    static_map_url = "https://maps.googleapis.com/maps/api/staticmap"
    center_lat = request.args.get('center_lat')
    center_lng = request.args.get('center_lng')
    roads_params = {'center': ','.join((center_lat, center_lng)),
        'format': 'png',
        'size': 'x'.join([str(WIDTH), str(HEIGHT)]),
        'maptype': 'roadmap',
        'sensor': 'false',
        'zoom': request.args.get('zoom'),
        'style': ['feature:road|element:labels|visibility:off', 'feature:transit.station|visibility:off', 'element:labels.text|visibility:off', 'feature:poi|visibility:off', 'feature:road|element:geometry.fill|color:0xff0000', 'feature:landscape.man_made|visibility:off', 'feature:road.highway|element:geometry.stroke|visibility:on|color:0xff0000|weight:8', 'feature:road.arterial|element:geometry.stroke|visibility:on|color:0xff0000|weight:6', 'feature:road.local|element:geometry.stroke|visibility:on|color:0xff0000|weight:4']
    }

    roads_url = '?'.join([static_map_url, urllib.urlencode(roads_params, doseq=True)])
    roads_static_maps_img = io.imread(roads_url) # reads as a numpy array
    percent_roads = get_percent_red(roads_static_maps_img)
    roads_image = get_roads_image(roads_static_maps_img)
    mh.imsave('foo.png', roads_image)
    roads_image = open('foo.png').read()
    
    # FIND BUILDINGS
    buildings_params = {'center': ','.join((center_lat, center_lng)),
        'format': 'png',
        'size': 'x'.join([str(WIDTH), str(HEIGHT)]),
        'maptype': 'roadmap',
        'sensor': 'false',
        'zoom': request.args.get('zoom'),
        'style': ['element:labels|visibility:off', 'feature:road|visibility:off', 'feature:poi|visibility:off', 'feature:transit|visibility:off', 'feature:water|visibility:off', 'feature:landscape.natural|visibility:off']
    }
    buildings_url = '?'.join([static_map_url, urllib.urlencode(buildings_params, doseq=True)])
    buildings_img = io.imread(buildings_url)
    percent_buildings = get_percent_building(buildings_img)
    buildings_image = get_building_image(buildings_img)
    # TODO also get building interiors, mash together
    mh.imsave('foo.png', buildings_image)
    buildings_image = open('foo.png').read()
    
    # FIND PERCENT GREEN
    satellite_params = {'center': ','.join((center_lat, center_lng)),
        'zoom': request.args.get('zoom'),
        'format': 'png',
        'size': 'x'.join([str(WIDTH), str(HEIGHT)]),
        'maptype': 'hybrid',
        'sensor': 'false',
        'style': 'visibility:off',
    }
    satellite_url = '?'.join([static_map_url, urllib.urlencode(satellite_params, doseq=True)])
    satellite_img = io.imread(satellite_url)
    
    percent_green = get_percent_green(satellite_img)
    green_image = get_green_image(satellite_img)
    mh.imsave('foo.png', green_image)
    green_image = open('foo.png').read()
    # TODO blah, f this! at the very least, use a stringio or something.

    return jsonify({'roads_image': base64.b64encode(roads_image),
                    'pct_roads': percent_roads,
                    'green_image': base64.b64encode(green_image),
                    'pct_green': percent_green,
                    'buildings_image': base64.b64encode(buildings_image),
                    'pct_buildings': percent_buildings})

if __name__=='__main__':
    app.run(debug=True)

