function setMapCenterAtCurrentPosition(map) {
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

function updateAllMarkersStatus(markers) {
    for (var i = 0; i < markers.length; i++) {
        updateMarkerStatus(i, markers[i]);
    }
}

function addMarker(markers, markerPosition) {
    // add new position to markers array
    markers.push(markerPosition);

    // update status after add
    updateMarkerStatus(markers.length-1, markerPosition);

    // show new route
    showRoute(markers);

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

function removeElement(element) {
    return element && element.parentNode && element.parentNode.removeChild(element);
}

function showRoute(markers) {
    var waypoints = [];
    var origin = markers[0];
    var destination = markers[markers.length - 1];

    for (var i = 1; i <= markers.length - 2; i++) {
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
        } else {
            // get last added element
            var marker = document.getElementById('marker_' + (markers.length - 1).toString());
            var result = removeElement(marker);

            if (result) {
                // delete last element
                markers.pop();
            }
        }
    });
}

function updateMapBounds(markers) {
    if (markers.length <= 0)
        return;

    var bounds = new google.maps.LatLngBounds();

    for (var i = 0; i < markers.length; i++) {
        // update bounds
        bounds.extend(markers[i]);
    }

    // center map
    map.fitBounds(bounds);
}
