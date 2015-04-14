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
//    var osm_content = osm_geojson.osm2geojson(data['osm_content']);
    var osm_content = data['megapolygon'];
    osm_content_demo = osm_content; // for debugging
    var geojson = JSON.parse(osm_content);
    map.data.addGeoJson(geojson);
    console.log(geojson.features);
//    map.data.addGeoJson(osm_content);
    // TODO Pick up here!
    // make sure you intersect this with the border of the map
    map.data.setStyle({
      fillColor: 'green',
      strokeWeight: 3
    });
    
    var statsText = "";
    var areaSum = 0;
    for (var i = 0; i < geojson.features.length; i++) {
      var feature = geojson.features[i];
//      var feature = geojson;
      if (!isPolygon(feature)) {
        continue;
      }
//      var type = whatIsIt(feature);
      var thisArea = area(feature);
    console.log(thisArea); // TODO why does this keep coming up with 0g
      areaSum += thisArea;
//      var thisThingText = "" + type + ", " + thisArea.toFixed(0) + "<br>";
//      statsText += thisThingText;
//      var coords = feature.geometry.coordinates[0][0];
//      var mapLabel = new MapLabel({
//          text: type,
//          position: new google.maps.LatLng(coords[1], coords[0]),
//          map: map,
//          fontSize: 12,
//          align: 'right'
//        });
//      mapLabel.set('position', new google.maps.LatLng(34.03, -118.235));
    }
    statsText += "Total area: " + areaSum.toFixed(0) + "<br>";
    test = areaSum;
    var mapArea = getMapArea(map);
    statsText += "Map area: " + mapArea.toFixed(0) + "<br>";
    statsText += "Percent covered: " + (areaSum / mapArea).toFixed(2) + "<br>";
    statsText += "Percent roads: " + data['pct_roads'].toFixed(2) + "<br>";
    statsText += "Percent green: " + data['pct_green'].toFixed(2) + "<br>";
    statsText += "Percent buildings: " + data['pct_buildings'].toFixed(2) + "<br>";
    $("#stats").html(statsText);
    console.log(data['roads_image_url']);
    $("#roads-image")[0].src = data['roads_image_url'];
    $("#green-image")[0].src = 'data:image/png;base64,' + data['green_image'];
    $("#buildings-image")[0].src = 'data:image/png;base64,' + data['buildings_image'];
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
      minZoom: 17,
      maxZoom: 19,
      center: new google.maps.LatLng(40.441667, -80),
      tilt: 0 // Disable 45-degree view of buildings.
    };
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    test = map;

  }

  initialize();
});