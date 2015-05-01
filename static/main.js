'use strict';

require.config({
  baseUrl: 'static/',
  paths: {
    jquery: 'jquery-1.11.2.min',
    google_maps: 'https://maps.googleapis.com/maps/api/js?v=3&libraries=geometry&key=AIzaSyDHVaCh9EcFtydDpNmpJyamhuv37APYQ_4',
    async: 'require-async',
    bootstrap: 'bootstrap.min',
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
  var locs = {};

  var generateStatsText = function(locations) {
    var statsText = "";
    for (var location in locations) {
      if (locations.hasOwnProperty(location)) {
        var vals = locations[location];
        statsText += location + ": ";
        statsText += "<span class='pct'>" + vals[0].toFixed(0) + "%</span> roads, ";
        statsText += "<span class='pct'>" + vals[1].toFixed(0) + "%</span> green, ";
        statsText += "<span class='pct'>" + vals[2].toFixed(0) + "%</span> buildings.";
        statsText += "<br>";
        statsText += "<span class='bar roads-bar' style='width:" + vals[0] * 3 + "px;'></span>";
        statsText += "<span class='bar green-bar' style='width:" + vals[1] * 3 + "px;'></span>";
        statsText += "<span class='bar buildings-bar' style='width:" + vals[2] * 3 + "px;'></span>";
        var otherPct = (100 - vals[0] - vals[1] - vals[2]);
        statsText += "<span class='bar other-bar' style='width:" + otherPct * 3 + "px;'></span>";
        statsText += "<br>";
      }
    }
    return statsText;
  }
  // I guess this is "we got some data, now do something".
  var showImage = function(data, textStatus, jqXHR) {
    $(".spinner").css("visibility", "hidden");
    var statsText = "";
    var key = "";
    if ($("#searchLocation").val().trim() == "") {
      var lat = map.getCenter().lat().toFixed(4);
      var lng = map.getCenter().lng().toFixed(4);
      key = "(" + lat + ", " + lng + ")";
    } else {
      key = $("#searchLocation").val().trim();
    }
    var pct_roads = data['pct_roads'].toFixed(2) * 100;
    var pct_green = data['pct_green'].toFixed(2) * 100;
    var pct_buildings = data['pct_buildings'].toFixed(2) * 100;
    locs[key] = [pct_roads, pct_green, pct_buildings];
    $("#stats").html(generateStatsText(locs));
    
    $("#roads-image")[0].src = 'data:image/png;base64,' + data['roads_image'];
    $("#green-image")[0].src = 'data:image/png;base64,' + data['green_image'];
    $("#buildings-image")[0].src = 'data:image/png;base64,' + data['buildings_image'];

  };

  var doit = function() {
    $(".spinner").css("visibility", "visible");
    var searchText = $("#searchLocation").val();
    if (searchText.trim() == '') {
      callServer();
    } else {
      geocoder.geocode({'address': searchText}, function(res, status) {
        map.setCenter(res[0].geometry.location);
        callServer();
      });
    }
  };
  
  var callServer = function() {
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
