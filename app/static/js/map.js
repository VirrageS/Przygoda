var poly;
var map;
var markers = [];

function initialize() {
    var mapOptions = {
        zoom: 13,
        center: new google.maps.LatLng(52.229937, 21.011380),
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };

    map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

    var polyOptions = {
        strokeColor: '#000000',
        strokeOpacity: 0.7,
        strokeWeight: 3,
        // editable: true
    };

    poly = new google.maps.Polyline(polyOptions);
    poly.setMap(map);

    // add a listener for the click event
    google.maps.event.addListener(map, 'click', function(event) {
        addMarker(event.latLng);
    });
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
    var path = poly.getPath();

    // add new waypoint on polyline
    path.push(markerPosition);

    // add a new marker at the new plotted point on the polyline.
    var marker = new google.maps.Marker({
        position: markerPosition,
        draggable: true,
        title: '#' + (path.getLength() - 1),
        map: map,
        animation: google.maps.Animation.DROP,
        number: path.getLength() - 1
    });

    // add new marker to markers array
    markers.push(marker);

    // update status after add
    updateMarkerStatus(marker.number, marker.getPosition());

    // add listener for dragend which handels updating polyline
    google.maps.event.addListener(marker, 'dragend', function() {
        path.setAt(this.number, this.getPosition());
        updateMarkerStatus(this.number, this.getPosition());
    });

    // add listener for right click which handels marker's deleting
    google.maps.event.addListener(marker, 'rightclick', function() {
        // remove marker from map and path
        path.removeAt(this.number);
        this.setMap(null);

        // delete marker from markers array
        var index = markers.indexOf(this);
        markers.splice(index, 1);

        for (var i = 0; i < markers.length; i++) {
            if (markers[i].getPosition() === path.getAt(i)) {
                // update marker number and status
                markers[i].number = i;
                markers[i].setTitle('#' + (i).toString());
                updateMarkerStatus(markers[i].number, markers[i].getPosition());
            }
        }
    });
}

google.maps.event.addDomListener(window, 'load', initialize);
