'use strict';
// api key: AIzaSyDHVaCh9EcFtydDpNmpJyamhuv37APYQ_4
// (function() {
  // var getBounds = function() {
  //  console.log("here are the bounds " + map.getBounds()) 
  // };
  var map;
  var showImage = function(data, textStatus, jqXHR) {
    var myImg = $('#static-map-image')[0];
    myImg.src = "data:image/png;base64," + data.image;
    var osm_content = osm_geojson.osm2geojson(data['osm_content']);
    map.data.addGeoJson(osm_content);
    
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
      mapTypeId: google.maps.MapTypeId.SATELLITE,
      tilt: 0 // Disable 45-degree view, e.g. of buildings downtown.
    };
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    // var canvas = document.getElementById('real-canvas');
    // var ctx = canvas.getContext('2d');
    // var myImg = document.getElementById('static-map-image');
    // canvas.height = myImg.height;
    // canvas.width = myImg.width;
    // ctx.drawImage(myImg, 0, 0, canvas.width, canvas.height);
    // var imgdata = ctx.getImageData(0, 0, canvas.width, canvas.height);
    // console.log("here is the imgdata");
    // console.log(imgdata);
  }

  google.maps.event.addDomListener(window, 'load', initialize);
// })();
