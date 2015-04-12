'use strict';
// (function() {

require.config({
  baseUrl: 'static/',
  paths: {
    jquery: 'jquery-1.11.2.min',
    google_maps: 'https://maps.googleapis.com/maps/api/js?v=3&libraries=geometry&key=AIzaSyDHVaCh9EcFtydDpNmpJyamhuv37APYQ_4',
    async: 'require-async',
//    maplabel: 'maplabel',
  },
  shim: {
    'maplabel': {
      deps: ['async!google_maps']
    }
  }
});

var osm_content_demo;
var test;

require(["osm_geojson", "jquery", "async!google_maps", "maplabel"], function() {

  var map;

  // Gets the area that is currently visible.
  var getMapArea = function(map) {
    var ne = map.getBounds().getNorthEast();
    var sw = map.getBounds().getSouthWest();
    var nw = new google.maps.LatLng(ne.lat(), sw.lng());
    var se = new google.maps.LatLng(sw.lat(), ne.lng());
    var corners = [ne, nw, sw, se, ne];
    return google.maps.geometry.spherical.computeArea(corners);
  };
  
  var getName = function(geojson_feature) {
    return geojson_feature.properties.name;
  }
  
  var whatIsIt = function(geojson_feature) {
    var props = geojson_feature.properties;
    if(props.amenity) {
      return "a " + props.amenity;
    } else if (props.shop) {
      return "a " + props.shop + " shop";
    } else if (props.highway) {
      return "a road";
    } else if (props['building:levels']){
      return "a " + props['building:levels'] + "-story building";
    } else if (props['demolished:building'] == 'yes') {
      return "a demolished building"
    } else {
      return "something";
    }
  };

  // Takes in a geojson feature, computes its area w/ google maps API.
  var area = function(feature) {
    var latLngArray = [];
    for (var i = 0; i < feature.geometry.coordinates[0].length; i++) {
      var arr = feature.geometry.coordinates[0][i];
      latLngArray.push(new google.maps.LatLng(arr[1], arr[0]));
    }
    return google.maps.geometry.spherical.computeArea(latLngArray);
  }

  // Returns true iff this thing is a closed polygon (representing a
  // building or other use of space).
  var isPolygon = function(geojson_feature) {
    return geojson_feature.geometry.type == "Polygon";
    // TODO multipolygons too?
  }
  
  // I guess this is "we got some OSM data, now do something".
  var showImage = function(data, textStatus, jqXHR) {
    var osm_content = osm_geojson.osm2geojson(data['osm_content']);
    osm_content_demo = osm_content;
    map.data.addGeoJson(osm_content);
    map.data.setStyle({
      fillColor: 'green',
      strokeWeight: 3
    });
    
    var statsText = "here are stats<br>";
    var areaSum = 0;
    for (var i = 0; i < osm_content.features.length; i++) {
      var feature = osm_content.features[i];
      if (!isPolygon(feature)) {
        continue;
      }
      var type = whatIsIt(feature);
      var thisArea = area(feature);
      areaSum += thisArea;
      var thisThingText = "" + type + ", " + thisArea.toFixed(0) + "<br>";
      statsText += thisThingText;
      var coords = feature.geometry.coordinates[0][0];
      var mapLabel = new MapLabel({
          text: type,
          position: new google.maps.LatLng(coords[1], coords[0]),
          map: map,
          fontSize: 12,
          align: 'right'
        });
//      mapLabel.set('position', new google.maps.LatLng(34.03, -118.235));
    }
    statsText += "Total area: " + areaSum.toFixed(0) + "<br>";
    test = areaSum;
    var mapArea = getMapArea(map);
    statsText += "Map area: " + mapArea.toFixed(0) + "<br>";
    statsText += "Percent covered: " + (areaSum / mapArea).toFixed(2) + "<br>";
    $("#stats").html(statsText);
  };

  var doit = function() {
    var sw = map.getBounds().getSouthWest();
    var ne = map.getBounds().getNorthEast();
    var center = map.getCenter();
    var zoom = map.getZoom();
    $.get("/image_for_map", {"sw_lat": sw.lat(), "sw_lng": sw.lng(),
        "ne_lat": ne.lat(), "ne_lng": ne.lng(),
        "center_lat": center.lat(), "center_lng": center.lng(),
        "zoom": zoom},
        showImage);
  };

  function initialize() {
    $("#doit").click(doit);

    var mapOptions = {
      zoom: 18,
      center: new google.maps.LatLng(40.441667, -80),
      tilt: 0 // Disable 45-degree view of buildings.
    };
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

  }

  initialize();
});