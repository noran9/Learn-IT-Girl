import requests
import geoip2.database
from django.shortcuts import render

def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
    except: 
        ip = ""
    if ip == '127.0.0.1':
        ip = '178.58.151.196'
    return ip


def index(request):
    url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=72f9d507e1f458a4e7a5ad8f19708420'
    reader = geoip2.database.Reader('C:/Users/norchi/Documents/Learn IT Girl/web-app/web_app/main/geolocation/GeoLite2-City_20190402/GeoLite2-City.mmdb')
    
    ip = get_client_ip(request)
    geo = reader.city(ip)

    r = requests.get(url.format(geo.location.latitude, geo.location.longitude)).json()

    location_weather = {
   	    'city' : geo.subdivisions.most_specific.name,
    	'clouds' : r['clouds']['all'],
    	'description' : r['weather'][0]['description'],
    	'icon': r['weather'][0]['icon'],
    }

    context = {'location_weather' : location_weather}

    return render(request,'index.html', context)