

import tkinter as tk
from tkinter import messagebox

from src.weather import get_weather_details, Weather

class WeatherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Weather App")
        self.master.geometry("300x250")

        # Create UI components
        self.city_label = tk.Label(master, text="Enter City:")
        self.city_label.pack(pady=10)

        self.city_entry = tk.Entry(master)
        self.city_entry.pack(pady=5)

        # Bind Enter key to the get_weather method
        self.city_entry.bind("<Return>", self.get_weather)

        self.search_button = tk.Button(master, text="Get Weather", command=self.get_weather)
        self.search_button.pack(pady=10)

        self.result_text = tk.Text(master, height=8, width=35)
        self.result_text.pack(pady=10)

    def get_weather(self, event=None):
        city = self.city_entry.get()
        try:
            current = get_weather_details(city)
        except Exception as e:
            messagebox.showerror("Error", f"City not found: {e}")
            pass
        self.display_weather(current)

    def display_weather(self, weather: Weather):
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        weather_desc = weather.weather_description
        temperature = weather.temperature
        humidity = weather.humidity
        wind_speed = weather.wind_speed

        result = (
            f"Weather in {weather.city}:\n"
            f"Description: {weather_desc}\n"
            f"Temperature: {temperature}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s\n"
        )
        
        self.result_text.insert(tk.END, result)