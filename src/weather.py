"""
Gathers all weather data that we need.

Takes the city as an argument and gathers detailed weather data. Classes included:
Weather
    Represents a weather state that any given moment
WeatherDay
    Collection of Weather moments spread throughout the day.
    Also holds and calculates temp max/mins and average weather conditions across the day.
WeatherMan
    Responsible for making the request to the Open Weather Map (OWM) API
    Collects and sorts the weather days that fall within it's specified forecast range
"""

from collections import defaultdict, Counter
import requests
import pycountry

from config import *

class Weather():
    """Standard weather, must include current temperature and other details."""
    def __init__(self, data=None):
        if data:
            self.populate_from_api(data)

    def populate_from_api(self, data: dict):
        """Populate the Weather object from API response data."""
        self.temperature = int(data['main']['temp'])
        self.humidity = data['main']['humidity']
        self.weather_description = data['weather'][0]['description']
        self.wind_speed = data['wind']['speed']
        self.timestamp = data.get('dt_txt')

class WeatherDay():
    """This class holds weather data for a single day."""
    def __init__(self):
        self.weather_objects: list[Weather] = []
        self.temp_high = float('-inf')
        self.temp_low = float('inf')
        self.total_humidity = 0
        self.total_wind_speed = 0
        self.average_humidity = 0
        self.average_wind_speed = 0
        self.most_common_description: str = "Clear" # Default to clear day

    def add_weather(self, weather):
        """Add a Weather object and update daily statistics."""
        self.weather_objects.append(weather)
        self.temp_high = max(self.temp_high, weather.temperature)
        self.temp_low = min(self.temp_low, weather.temperature)
        self.total_humidity += weather.humidity
        self.total_wind_speed += weather.wind_speed

    def calculate_averages(self):
        """Calculate average humidity and wind speed."""
        weather_description_counter = Counter()
        c = len(self.weather_objects)
        if c > 0:
            self.average_humidity = self.total_humidity / c
            self.average_wind_speed = self.total_wind_speed / c
        
            for weather in self.weather_objects:
                weather_description_counter[weather.weather_description] += 1

        # Get the most common weather description
        self.most_common_description = weather_description_counter.most_common(1)[0][0]

        return self.average_humidity, self.average_wind_speed, self.most_common_description

class WeatherMan():
    """This will be the general weather gatherer that will ask for a report on the weather."""

    def __init__(self, city, pretty_name=None):
        self.city: str = city
        self.pretty_name: str = pretty_name
        self.current_weather: Weather = None
        self.forecast: list[WeatherDay] = []  # List to hold WeatherDay objects

        self.fetch_forecast()  # Fetch the forecast immediately after fetching current weather

    def fetch_weather(self):
        """We may use this if we care about being more accurate to hit a more accurate endpoint for current weather.

        Raises:
            Exception: _description_
        """
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': self.city,
            'appid': API_KEY,
            'units': 'imperial'  # Use 'imperial' for Fahrenheit
        }
        
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.current_weather = Weather()
            self.current_weather.populate_from_api(data)
        else:
            raise Exception(f"Error fetching weather data: {response.status_code} - {response.json().get('message')}")


    def fetch_forecast(self):
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': self.city,
            'appid': API_KEY,
            'units': 'imperial'
        }
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            self.forecast = self.process_forecast_data(data['list'])
        else:
            raise Exception(f"Error fetching forecast data: {response.status_code} - {response.json().get('message')}")

    def process_forecast_data(self, forecast_list) -> list[WeatherDay]:
        """Takes the raw forecast data returned from the API request and creates WeatherDay's according to the data.

        Args:
            forecast_list: The part of the data object that contains the forecast reports across multiple days.

        Returns:
            list[WeatherDay]: The days of weather that are captured within this forecast report.
        """
        weather_days = defaultdict(WeatherDay)

        for entry in forecast_list:
            weather = Weather(entry)
            if not self.current_weather:
                # We don't have a weather yet, so this must be the closest to our current weather.
                self.current_weather = weather
            date = entry['dt_txt'].split(" ")[0]  # Extract date part

            weather_days[date].add_weather(weather)

        # Calculate averages for each WeatherDay
        for weather_day in weather_days.values():
            weather_day.calculate_averages()

        return list(weather_days.values())  # Convert defaultdict to list of WeatherDay objects

def get_owm_query(city_input: str) -> str:
    """Creates a OWM compatible query out of a formal Geoname city.

    e.g. Turns "Moscow, Idaho, United States" into "Moscow,ID,US"

    Details:
        This is important because if we just gave OWM "Moscow, Idaho, United States"
        it would just look for Moscow, Russia. This is because the OWM API doesn't recognize
        the state and country code following the city name (it expects 2 letter formats),
        so it just throws those out and pretends like it didn't see them.

        Then when we go to search up just "Moscow" for cities, the multi million
        population city of Moscow, Russia comes up before the 26k pop Moscow, Idaho, surprisingly.

        This is one of the weaker parts of this project, and if this were anything larger than a
        small toy example, I would 100% rework the
            City name search -> select on UI -> feed to this file -> convert search to OWM readable query -> make OWM request
        pipline. But, time is precious.
        
    Args:
        city_input (str): The Geoname string representing the city name.

    Returns:
        str: OWM Compatible query
    """
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

def get_weather_man(city: str) -> WeatherMan:
    query = get_owm_query(city)
    weather = WeatherMan(query)
    return weather