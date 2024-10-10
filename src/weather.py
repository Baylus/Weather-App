"""
Just for getting the weather data that we need.
"""

import requests
import pycountry

from config import *

class Weather():
    """Standard weather, must include current temperature 
    """
    def __init__(self, city, pretty_name = None):
        self.city = city
        self.pretty_name = pretty_name
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
            print("We failed to fetch weather data")
            raise Exception(f"Error fetching weather data: {response.status_code} - {response.json().get('message')}")

    def display_weather(self):
        # Try to print out the prettier version if we have it.
        print(f"Weather in {self.pretty_name if self.pretty_name else self.city}:")
        print(f"  Description: {self.weather_description}")
        print(f"  Temperature: {self.temperature}°F")
        print(f"  Humidity: {self.humidity}%")
        print(f"  Wind Speed: {self.wind_speed} m/s")


def get_owm_query(city_input: str) -> str:
    # Check if the input is just a single city name
    if ',' not in city_input:
        return city_input.strip()  # No transformation needed

    # Split the input by commas and strip whitespace
    parts = [part.strip() for part in city_input.split(',')]
    
    city = parts[0]  # First part is always the city

    if len(parts) == 3:  # Format: "City, State, Country"
        state_name = parts[1]
        country_name = parts[2]

        # Get the state code
        state_code = get_state_code(state_name)
        # Get the country code
        country_code = get_country_code(country_name)
        
        return f"{city},{state_code},{country_code}"

    elif len(parts) == 2:  # Format: "City, Country"
        country_name = parts[1]
        country_code = get_country_code(country_name)

        return f"{city},{country_code}"

    return city.strip()  # Default case (single city without additional info)

def get_state_code(state_name: str, country_code='US'):
    for state in pycountry.subdivisions.get(country_code=country_code):
        if state.name.lower() == state_name.lower():
            return state.code.split('-')[1]  # Extract state code
    return None

def get_country_code(country_name: str):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2  # Return the alpha-2 code
    except LookupError:
        return None

def get_weather_details(city: str) -> Weather:
    query = get_owm_query(city)
    weather = Weather(query)
    return weather