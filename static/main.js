'use strict';

require.config({
  baseUrl: 'static/',
  paths: {
    jquery: 'jquery-1.11.2.min',
    google_maps: 'https://maps.googleapis.com/maps/api/js?v=3&libraries=geometry&key=AIzaSyDHVaCh9EcFtydDpNmpJyamhuv37APYQ_4',
    async: 'require-async',
  },
  shim: {
    'maplabel': {
      deps: ['async!google_maps']
    }
  }
});


require(["jquery", "async!google_maps"], function() {

  var map;
  var geocoder = new google.maps.Geocoder();

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
    statsText += "This place is: ";
    statsText += "Percent roads: " + data['pct_roads'].toFixed(2) * 100 + "<br>";
    statsText += "Percent green: " + data['pct_green'].toFixed(2) * 100 + "<br>";
    statsText += "Percent buildings: " + data['pct_buildings'].toFixed(2) * 100 + "<br>";
    $("#stats").html(statsText);
    console.log(statsText);
    $("#roads-image")[0].src = 'data:image/png;base64,' + data['roads_image'];
    $("#green-image")[0].src = 'data:image/png;base64,' + data['green_image'];
    $("#buildings-image")[0].src = 'data:image/png;base64,' + data['buildings_image'];
  };

  var doit = function() {
    var searchText = $("#searchLocation").val();
    if (searchText.trim() == '') {
      call_server();
    } else {
      geocoder.geocode({'address': searchText}, function(res, status) {
        map.setCenter(res[0].geometry.location);
        call_server();
      });
    }
  };
  
  var call_server = function() {
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
    
    $("#chkGreen").click(function() {
      if ($("#chkGreen").prop("checked")) {
        $("#green-image").show();
      } else {
        $("#green-image").hide();
      }
    });
    $("#chkBldgs").click(function() {
      if ($("#chkBldgs").prop("checked")) {
        $("#buildings-image").show();
      } else {
        $("#buildings-image").hide();
      }
    });
    $("#chkRoads").click(function() {
      if ($("#chkRoads").prop("checked")) {
        $("#roads-image").show();
      } else {
        $("#roads-image").hide();
      }
    });
  }

  initialize();
});