#!/usr/bin/env python

import requests, cStringIO

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
    # TODO figure out the bounds of this image
    return r

if __name__=='__main__':
    get_static_map(40.441667, -80)

