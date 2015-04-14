#!/usr/bin/env python

import requests, cStringIO, base64, pprint, urllib, time, json
from flask import Flask, render_template, jsonify, request
import numpy as np, mahotas as mh
import matplotlib.pyplot as plt
from skimage import io
import skimage.color
import osmread
from shapely.geometry import Point, Polygon
import shapely.ops, shapely.geometry

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
    
# img is a numpy array, WIDTH x HEIGHT x 3 (rgb).
def get_percent_red(img):
    # numpy: * is per-item.
    # uses anything where red > 250 b/c I'm not sure why I told it red
    # is #ff0000 but it's giving me red=254.
    n_red = sum(sum((img[:,:,0]>250)*(img[:,:,1] == 0)*(img[:,:,2]==0)))
    return n_red * 1.0 / (WIDTH * HEIGHT)

def get_green_image(img):
    imghsv = skimage.color.rgb2hsv(img)
    greenpixels = (imghsv[:,:,0] > .2) * (imghsv[:,:,0] < .7) * (imghsv[:,:,1] > .1)
    greenpixels = mh.gaussian_filter(greenpixels, 3) > .5
    img[-greenpixels] = [255,255,255]
    return img
  
def get_percent_building(img):
    # 242 240 233 is the interior building RGB.
    # 242 238 226 is close too.
    # 233 229 220 is background.
    bldg = (img[:,:,0]==242) * (img[:,:,1]==240) * (img[:,:,2]==233)
    bldg2 = (img[:,:,0]==242) * (img[:,:,1]==238) * (img[:,:,2]==226)
    return sum(sum(np.logical_or(bldg, bldg2))) * 1.0 / (WIDTH * HEIGHT)
  
def get_building_image(img):
    bldg = (img[:,:,0]==242) * (img[:,:,1]==240) * (img[:,:,2]==233)
    bldg2 = (img[:,:,0]==242) * (img[:,:,1]==238) * (img[:,:,2]==226)
    bldg_pixels = np.logical_or(bldg, bldg2)
    bldg_pixels = mh.gaussian_filter(bldg_pixels, 3) > .5
    img[-bldg_pixels] = [0,0,0]
    return img
  
# img is a numpy array, WIDTH x HEIGHT x 3 (rgb).
# Returns the number of pixels that are _some kind of_ green. A little
# inexact because who knows exactly what green color you've got.
def get_percent_green(img):
    imghsv = skimage.color.rgb2hsv(img)
    greenpixels = (imghsv[:,:,0] > .2) * (imghsv[:,:,0] < .7) * (imghsv[:,:,1] > .1)
    greenpixels = mh.gaussian_filter(greenpixels, 3) > .5
    print sum(sum(greenpixels)) * 1.0 / (640*640)
    return sum(sum(greenpixels)) * 1.0 / (640*640)

@app.route("/image_for_map")
def get_image_for_map():
    osm_url = "http://api.openstreetmap.org/api/0.6/map"
    left = request.args.get('sw_lng')
    bottom = request.args.get('sw_lat')
    right = request.args.get('ne_lng')
    top = request.args.get('ne_lat')
    osm_params = {'bbox': ','.join((left, bottom, right, top))}
    osm_res = requests.get(osm_url, params=osm_params)
#    print osm_res.content
    outfile = open('foo.osm', 'w') # TODO ugh
    outfile.write(osm_res.content)
    outfile.close()
    nodes = {} # node ID -> (lon, lat) pair - (x, y) like shapely.
    ways = []
    polygons = []
    for entity in osmread.parse_file('foo.osm'):
        if isinstance(entity, osmread.Node):
            nodes[entity.id] = (entity.lon, entity.lat)
        elif isinstance(entity, osmread.Way):
            ways.append(entity)

    for way in ways:
        if 'building' not in way.tags:
            continue
        node_ids = way.nodes
        points = [nodes[id] for id in node_ids]
        if len(points) < 3:
            continue
        newpoly = Polygon(points)
        if newpoly.is_valid: # TODO why are some polygons invalid?
            polygons.append(newpoly)
    megapolygon = shapely.ops.cascaded_union(polygons)


    # FIND PERCENT ROADS
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
    roads_img = io.imread(roads_url) # reads as a numpy array
    percent_roads = get_percent_red(roads_img)
    
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

    #    print json.dumps({'type': 'Feature', 'properties':{}, 'geometry': shapely.geometry.mapping(megapolygon)})
    
    return jsonify({'osm_content': osm_res.content,
                    'megapolygon': json.dumps({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'geometry': shapely.geometry.mapping(megapolygon)}]}),
                    'roads_image_url': roads_url,
                    'pct_roads': percent_roads,
                    'green_image': base64.b64encode(green_image),
                    'pct_green': percent_green,
                    'buildings_image': base64.b64encode(buildings_image),
                    'pct_buildings': percent_buildings})

if __name__=='__main__':
    app.run(debug=True)

