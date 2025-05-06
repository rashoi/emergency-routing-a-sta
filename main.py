import googlemaps
import heapq
from math import radians, sin, cos, sqrt, atan2
from time import time
from IPython.display import HTML, display

API_KEY = 'AIzaSyCJD3zGTWBY-_QwgCL3w0eKClNmo4gqnTg'
gmaps = googlemaps.Client(key=API_KEY)

route_cache = {}

def get_route_details(origin, destination):
    key = (origin, destination)
    if key in route_cache:
        return route_cache[key]
    try:
        directions = gmaps.directions(origin, destination, departure_time='now')
        route = directions[0]['legs'][0]
        distance = route['distance']['value']
        duration = route['duration']['value']
        route_cache[key] = (distance, duration)
        return distance, duration
    except Exception as e:
        print(f"Error fetching route details: {e}")
        return float('inf'), float('inf')

def get_hospitals(location):
    hospitals = gmaps.places_nearby(location=location, radius=5000, type='hospital')
    return [(hospital['name'], hospital['geometry']['location']['lat'], hospital['geometry']['location']['lng']) for hospital in hospitals.get('results', [])]

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = radians(coord1[0]), radians(coord1[1])
    lat2, lon2 = radians(coord2[0]), radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

accident_location = input("Enter the accident location (e.g., your current location): ")
geocode_accident = gmaps.geocode(accident_location)

if geocode_accident:
    accident_coords = (geocode_accident[0]['geometry']['location']['lat'], geocode_accident[0]['geometry']['location']['lng'])
    hospitals = get_hospitals(accident_coords)
    if hospitals:
        nearest_hospital = min(hospitals, key=lambda h: haversine(accident_coords, (h[1], h[2])))
        nearest_hospital_name, nearest_hospital_lat, nearest_hospital_lng = nearest_hospital
        distance, duration = get_route_details(accident_coords, (nearest_hospital_lat, nearest_hospital_lng))
        print(f"Nearest Hospital: {nearest_hospital_name}")
        print(f"Distance to nearest hospital: {distance / 1000:.2f} km")
        print(f"Estimated travel time: {duration / 60:.0f} minutes")
        html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>Route to Nearest Hospital</title>
    <style>
        #map {{
            height: 100vh;
            width: 100%;
        }}
    </style>
    <script>
        function initMap() {{
            var map = new google.maps.Map(document.getElementById('map'), {{
                zoom: 14,
                center: {{lat: {accident_coords[0]}, lng: {accident_coords[1]}}}
            }});

            var accidentLocation = {{lat: {accident_coords[0]}, lng: {accident_coords[1]}}};
            var accidentMarker = new google.maps.Marker({{
                position: accidentLocation,
                map: map,
                title: 'Accident Location'
            }});

            var hospitalLocation = {{lat: {nearest_hospital_lat}, lng: {nearest_hospital_lng}}};
            var hospitalMarker = new google.maps.Marker({{
                position: hospitalLocation,
                map: map,
                title: '{nearest_hospital_name}'
            }});

            var request = {{
                origin: accidentLocation,
                destination: hospitalLocation,
                travelMode: 'DRIVING'
            }};
            
            var directionsService = new google.maps.DirectionsService();
            var directionsRenderer = new google.maps.DirectionsRenderer({{
                polylineOptions: {{ strokeColor: '#FF0000' }} 
            }});
            directionsRenderer.setMap(map);

            directionsService.route(request, function(result, status) {{
                if (status === 'OK') {{
                    directionsRenderer.setDirections(result);
                }}
            }});
        }}
    </script>
    <script async defer src="https://maps.googleapis.com/maps/api/js?key={'AIzaSyCJD3zGTWBY-_QwgCL3w0eKClNmo4gqnTg'}&callback=initMap"></script>
</head>
<body>
    <div id="map"></div>
</body>
</html>
        '''
        display(HTML(html_content))
    else:
        print("No hospitals found nearby the accident location.")
else:
    print("Could not find geocoding for the provided accident location.")
