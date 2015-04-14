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

require(["jquery", "async!google_maps", "maplabel"], function() {

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

  // I guess this is "we got some data, now do something".
  var showImage = function(data, textStatus, jqXHR) {
    var mapArea = getMapArea(map);
    var statsText = "";
    statsText += "Map area: " + mapArea.toFixed(0) + "<br>";
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
  }

  initialize();
});