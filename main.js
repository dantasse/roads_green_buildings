'use strict';
// api key: AIzaSyDHVaCh9EcFtydDpNmpJyamhuv37APYQ_4
// (function() {
  var getBounds = function() {
   console.log("here are the bounds " + map.getBounds()) 
  }
  var map;
  var doit = function() {
    alert(map.getBounds());
  }
  function initialize() {
    $("#doit").click(doit);

    var mapOptions = {
      zoom: 18,
      center: new google.maps.LatLng(40.441667, -80),
      mapTypeId: google.maps.MapTypeId.SATELLITE,
      tilt: 0, // Disable 45-degree view, e.g. of buildings downtown.
    };
    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    console.log("here are the zoom " + map.getZoom());
    console.log("map type: " + map.getMapTypeId());
    console.log("here are the center " + map.getCenter());
    console.log("getting bounds...");

    var canvas = document.getElementById('real-canvas');
    var ctx = canvas.getContext('2d');
    var myImg = document.getElementById('static-map-image');
    canvas.height = myImg.height;
    canvas.width = myImg.width;
    ctx.drawImage(myImg, 0, 0, canvas.width, canvas.height);
    // var imgdata = ctx.getImageData(0, 0, canvas.width, canvas.height);
    // console.log("here is the imgdata");
    // console.log(imgdata);
  }

  google.maps.event.addDomListener(window, 'load', initialize);
// })();
