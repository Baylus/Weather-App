"""
Just for getting the weather data that we need.
"""

import json # Temp Pretty print

import requests

with open("API_KEY", "r") as f:
    API_KEY = f.read()

class Weather():
    """Standard weather, must include current temperature 
    """
    def __init__(self, city):
        self.city = city
        self.temperature = None
        self.humidity = None
        self.weather_description = None
        self.wind_speed = None
        self.fetch_weather()

    def fetch_weather(self):
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': self.city,
            'appid': API_KEY,
            'units': 'imperial'  # Use 'imperial' for Fahrenheit
        }
        
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            self.temperature = data['main']['temp']
            self.humidity = data['main']['humidity']
            self.weather_description = data['weather'][0]['description']
            self.wind_speed = data['wind']['speed']
        else:
            raise Exception(f"Error fetching weather data: {response.status_code} - {response.json().get('message')}")

    def display_weather(self):
        print(f"Weather in {self.city}:")
        print(f"  Description: {self.weather_description}")
        print(f"  Temperature: {self.temperature}°F")
        print(f"  Humidity: {self.humidity}%")
        print(f"  Wind Speed: {self.wind_speed} m/s")


def get_weather_details(city: str) -> Weather:
    weather = Weather(city)
    return weather