import requests, json
import geoip2.database
import datetime as dt
import pandas as pd
import pickle
from django.shortcuts import render
from django.http import HttpResponse
from django import forms
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateEntry


def prediction(img):
    if img is None:
        predict = ""
        return predict
    # Replace with a valid key
    training_key = "b5bfc9d99f13452283d32d34b6fdaf91"
    prediction_key = "667bfe4caf614b7ab5d493d108310c31"
    prediction_resource_id = "/subscriptions/43d04aaa-f089-471d-93c4-2db4cfcb099e/resourceGroups/newresource/providers/Microsoft.CognitiveServices/accounts/newresource_prediction"
    project_id = "8b296d37-4100-4836-9441-a7d5a1f8ac1f"

    ENDPOINT = "https://westeurope.api.cognitive.microsoft.com/customvision/v3.0/Prediction/8b296d37-4100-4836-9441-a7d5a1f8ac1f/classify/iterations/Iteration1/url"
    #base_image_url = "C:/Users/norchi/Documents/Learn IT Girl/"
    #image =  open(base_image_url + "stars/heic1303b.jpg", "rb")
    image = {'url' : img}
    
    #Htttp request
    headers = {
        'Prediction-Key': prediction_key,
        'Content-Type': 'application/json',
    }

    response = requests.request('POST', ENDPOINT, data=None, json=image, headers=headers).json()
    #parsed = json.loads(response.text)
    #predictions = parsed['predictions']
    name = response['predictions'][0]['tagName']
    probability = response['predictions'][0]['probability']

    predict = "This image is a " + name + " with a probability of: {0:.2f}%".format(probability * 100)
    return predict

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
    image = None
    if request.method == 'POST':
        #form = ContactForm(request.POST)
        image = request.POST['url']
        #return render(request,'index.html', context)

    url = 'http://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid=72f9d507e1f458a4e7a5ad8f19708420'
    reader = geoip2.database.Reader('C:/Users/norchi/Documents/Learn IT Girl/web-app/web_app/main/geolocation/GeoLite2-City_20190402/GeoLite2-City.mmdb')
    
    ip = get_client_ip(request)
    geo = reader.city(ip)

    r = requests.get(url.format(geo.location.latitude, geo.location.longitude)).json()

    url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt=2019-05-28"
    g = str(geo.location.latitude) + "," + str(geo.location.longitude)
    JSONContent = requests.get(url.format(g)).json()
    content = json.dumps(JSONContent, indent = 4, sort_keys=True)

    #Current weather
    location_weather = {
   	    'city' : geo.subdivisions.most_specific.name,
        'clouds' : r['clouds']['all'],
        'description' : r['weather'][0]['description'],
        'icon': r['weather'][0]['icon'],
    }

    #Microsoft custom vision prediction
    predict = prediction(image)

    #8 hour cloud cover prediction
    hour = dt.datetime.now().hour
    day = dt.datetime.now().day
    new = [geo.subdivisions.most_specific.name, day, hour]
    date = dt.datetime.today().strftime("%Y-%m-%d")

    url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt={}&hour="+str(hour)
    JSONContent = requests.get(url.format(geo.subdivisions.most_specific.name, date)).json()
    Temperature = JSONContent['forecast']['forecastday'][0]['hour'][0]['temp_c']
    Pressure = JSONContent['forecast']['forecastday'][0]['hour'][0]['pressure_mb']
    Humidity = JSONContent['forecast']['forecastday'][0]['hour'][0]['humidity']
    Cloud_cover = JSONContent['forecast']['forecastday'][0]['hour'][0]['cloud']

    new.append(Temperature)
    new.append(Pressure)
    new.append(Humidity)
    new.append(Cloud_cover)

    for i in range(hour - 8, hour - 1):
        url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt={}&hour="+str(i)
        JSONContent = requests.get(url.format(geo.subdivisions.most_specific.name, date)).json()
        Temperature = JSONContent['forecast']['forecastday'][0]['hour'][0]['temp_c']
        new.append(Temperature)

    for i in range(hour - 8, hour - 1):
        url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt={}&hour="+str(i)
        JSONContent = requests.get(url.format(geo.subdivisions.most_specific.name, date)).json()
        Pressure = JSONContent['forecast']['forecastday'][0]['hour'][0]['pressure_mb']
        new.append(Pressure)
        
    for i in range(hour - 8, hour - 1):
        url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt={}&hour="+str(i)
        JSONContent = requests.get(url.format(geo.subdivisions.most_specific.name, date)).json()
        Humidity = JSONContent['forecast']['forecastday'][0]['hour'][0]['humidity']
        new.append(Humidity)
        
    for i in range(hour - 8, hour - 1):
        url = "http://api.apixu.com/v1/history.json?key=f87b86729047441786b83603190105&q={}&dt={}&hour="+str(i)
        JSONContent = requests.get(url.format(geo.subdivisions.most_specific.name, date)).json()
        Cloud_cover = JSONContent['forecast']['forecastday'][0]['hour'][0]['cloud']
        new.append(Cloud_cover)
    new_data = pd.DataFrame([new], columns = ['City', 'Day in May 2019', 'Hour', 'Temperature', 'Pressure', 'Humidity', 'Cloud cover', 'Temperature_1', 'Temperature_2', 'Temperature_3', 'Temperature_4', 'Temperature_5', 'Temperature_6', 'Temperature_7', 'Pressure_1', 'Pressure_2', 'Pressure_3','Pressure_4', 'Pressure_5','Pressure_6', 'Pressure_7', 'Humidity_1', 'Humidity_2', 'Humidity_3', 'Humidity_4', 'Humidity_5', 'Humidity_6', 'Humidity_7', 'Cloud cover_1', 'Cloud cover_2', 'Cloud cover_3', 'Cloud cover_4', 'Cloud cover_5', 'Cloud cover_6', 'Cloud cover_7'])

    filename = 'C:/Users/norchi/Documents/Learn IT Girl/model/finalized_model.sav'
    regressor = pickle.load(open(filename, 'rb'))

    #Chosen features with more than 0.5 correlation
    predictors = ['Cloud cover_1', 'Cloud cover_2', 'Cloud cover_3', 'Cloud cover_4', 'Cloud cover_5', 'Cloud cover_6','Cloud cover_7', 'Pressure', 'Pressure_1', 'Pressure_2', 'Pressure_3', 'Pressure_4']
    X = new_data[predictors]
    hour_predict = regressor.predict(X)[0].round()

    context = {
    'location_weather' : location_weather,
    'prediction' : predict,
    'hour_predict': str(hour_predict)}

    return render(request,'index.html', context)
