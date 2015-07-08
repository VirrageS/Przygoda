var rendererOptions = {
    draggable: true,
    preserveViewport: true,
    suppressBicyclingLayer: true,

    polylineOptions: {
        strokeColor: '#6CA4FB',
        strokeWeight: 6,
        strokeOpacity: 0.95,
        clickable: false,
        draggable: false,
        editable: false
    }
    // suppressMarkers : true
};
var directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
var directionsService = new google.maps.DirectionsService();

var map;

var markers = [];

function initialize() {
    var mapOptions = {
        zoom: 13,
        center: new google.maps.LatLng(52.229937, 21.011380),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
    directionsDisplay.setMap(map);

    google.maps.event.addListener(directionsDisplay, 'directions_changed', function() {
        // compute total distance
        computeTotalDistance(directionsDisplay.getDirections());

        // get legs from route
        var legs = directionsDisplay.getDirections().routes[0].legs;

        // update all points
        for (var i = 0; i < legs.length; i++) {
            markers[i + 1] = legs[i].end_location;
            updateMarkerStatus(i + 1, legs[i].end_location);
        }

        // update origin
        markers[0] = legs[0].start_location;
        updateMarkerStatus(0, legs[0].start_location);
    });

    // add a listener for the click event
    google.maps.event.addListener(map, 'click', function(event) {
        addMarker(event.latLng);
    });
}

function locateCurrentPosition() {
    if (navigator.geolocation) {
        success = function(position) {
            map.setCenter(new google.maps.LatLng(position.coords.latitude, position.coords.longitude));
        };
        error = function() {}

        navigator.geolocation.getCurrentPosition(success, error);
    }
}

// compute total distance of path
function computeTotalDistance(result) {
    var total = 0;
    var myroute = result.routes[0];
    for (var i = 0; i < myroute.legs.length; i++) {
        total += myroute.legs[i].distance.value;
    }

    total = total / 1000.0;
    document.getElementById('total-distance').innerHTML = total + ' km';
}

// updates marker input value which will be passed
function updateMarkerStatus(number, position) {
    var markerStatus = document.getElementById('marker_' + number.toString());

    if (markerStatus) {
        markerStatus.value = position;
    } else {
        var input = document.createElement("input");
        input.id = 'marker_' + number.toString();
        input.name = 'marker_' + number.toString();
        input.type = "hidden";
        input.value = position;

        document.getElementById("markers").appendChild(input);
    }
}

function addMarker(markerPosition) {
    // add new position to markers array
    markers.push(markerPosition);

    // update status after add
    updateMarkerStatus(markers.length-1, markerPosition);

    // show new route
    showRoute();

    // add listener for right click which handels marker's deleting
    // google.maps.event.addListener(marker, 'rightclick', function() {
    //     // remove marker from map and path
    //     path.removeAt(this.number);
    //     this.setMap(null);
    //
    //     // delete marker from markers array
    //     var index = markers.indexOf(this);
    //     markers.splice(index, 1);
    //
    //     for (var i = 0; i < markers.length; i++) {
    //         if (markers[i].getPosition() === path.getAt(i)) {
    //             // update marker number and status
    //             markers[i].number = i;
    //             markers[i].setTitle('#' + (i).toString());
    //             updateMarkerStatus(markers[i].number, markers[i].getPosition());
    //         }
    //     }
    // });
}

function showRoute() {
    var waypoints = [];
    var origin = markers[0];
    var destination = markers[markers.length-1];

    for (var i = 1; i < markers.length - 2; i++) {
        waypoints.push({location: markers[i], stopover: true});
    }

    var request = {
        origin: origin,
        destination: destination,
        waypoints: waypoints,
        optimizeWaypoints: false,
        travelMode: google.maps.TravelMode.BICYCLING // BICYCLING, DRIVING
    };

    directionsService.route(request, function(response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
        }
    });
}

google.maps.event.addDomListener(window, 'load', initialize);
