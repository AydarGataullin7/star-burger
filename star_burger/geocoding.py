import os
import requests
from geopy.distance import geodesic
from places.models import Place


def fetch_coordinates(address, apikey=None):
    try:
        place = Place.objects.get(address=address)
        if place.latitude and place.longitude:
            return place.longitude, place.latitude
    except Place.DoesNotExist:
        pass

    if apikey is None:
        apikey = os.getenv('YANDEX_GEOCODER_API_KEY')

    if not apikey:
        raise ValueError("YANDEX_GEOCODER_API_KEY is required")

    base_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(base_url, params={
        'geocode': address,
        'apikey': apikey,
        'format': 'json',
    })
    response.raise_for_status()

    found_places = response.json(
    )['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        Place.objects.get_or_create(address=address, defaults={
                                    'latitude': None, 'longitude': None})
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

    Place.objects.update_or_create(
        address=address,
        defaults={
            'latitude': float(lat),
            'longitude': float(lon)
        }
    )

    return lon, lat


def calculate_distance(coords1, coords2):
    if not coords1 or not coords2:
        return None

    point1 = (float(coords1[1]), float(coords1[0]))
    point2 = (float(coords2[1]), float(coords2[0]))

    return geodesic(point1, point2).km
