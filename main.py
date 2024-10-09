"""
Retrieve weather details for a given city.
"""
import tkinter as tk


from src.weather import get_weather_details, Weather
from src.gui import WeatherApp


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()