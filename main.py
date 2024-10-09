"""
Retrieve weather details for a given city.
"""

from src.weather import get_weather_details, Weather

if __name__ == "__main__":
    city = input("Find weather for city: ")
    current: Weather = get_weather_details(city)
    current.display_weather()
    pass