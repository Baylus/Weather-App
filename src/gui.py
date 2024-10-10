

import requests
import tkinter as tk
from tkinter import messagebox, Listbox, StringVar

from config import *
from src.weather import get_weather_details, Weather

class WeatherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Weather App")
        self.master.geometry("400x450")

        self.city_label = tk.Label(master, text="Enter City:")
        self.city_label.pack(pady=10)

        self.city_var = StringVar()
        self.city_entry = tk.Entry(master, textvariable=self.city_var)
        self.city_entry.pack(pady=5)
        
        # Listbox for showing suggestions
        self.suggestions_box = Listbox(master)
        self.suggestions_box.pack(pady=5, fill=tk.BOTH)

        self.city_entry.bind("<KeyRelease>", self.debounce_suggestions)

        self.suggestions_box.bind("<<ListboxSelect>>", self.on_select)

        self.search_button = tk.Button(master, text="Get Weather", command=self.get_weather)
        self.search_button.pack(pady=10)

        self.result_text = tk.Text(master, height=8, width=50)
        self.result_text.pack(pady=10)

        self.city_data = []  # To store city suggestions
        self.debounce_timer = None  # To store the timer reference

    def debounce_suggestions(self, event=None):
        if self.debounce_timer is not None:
            self.master.after_cancel(self.debounce_timer)  # Cancel the previous timer
        
        # Set a new timer
        self.debounce_timer = self.master.after(1000, self.get_suggestions)  # 1000ms debounce time


    def get_suggestions(self, event=None):
        city = self.city_var.get()
        if city:
            api_url = f"http://api.geonames.org/searchJSON?q={city}&maxRows=10&username={GEONAMES_USERNAME}"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                self.suggestions_box.delete(0, tk.END)  # Clear previous suggestions
                self.city_data = []  # Clear previous city data
                for item in data.get('geonames', []):
                    name = item['name']
                    state = item.get('adminName1', '')  # Use adminName1 for state
                    country = item['countryName']  # Use countryName for country
                    display_name = f"{name}, {state}, {country}" if state else f"{name}, {country}"
                    self.suggestions_box.insert(tk.END, display_name)
                    self.city_data.append((name, state, country))
            else:
                self.suggestions_box.delete(0, tk.END)  # Clear suggestions if API fails

    def on_select(self, event):
        selected = self.suggestions_box.curselection()
        if selected:
            city_name, state, country = self.city_data[selected[0]]
            # CONSIDER: Trying to store the detailed object that geonames gives us if we struggle with matching city identity.
            self.city_var.set(f"{city_name}, {state}, {country}" if state else f"{city_name}, {country}")
            self.suggestions_box.delete(0, tk.END)  # Clear suggestions

    def get_weather(self, event=None):
        city = self.city_var.get()
        try:
            current = get_weather_details(city)
        except Exception as e:
            messagebox.showerror("Error", f"City not found: {e}")
            pass
        self.display_weather(current, city)

    def display_weather(self, weather: Weather, city_name: str = ""):
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        weather_desc = weather.weather_description
        temperature = weather.temperature
        humidity = weather.humidity
        wind_speed = weather.wind_speed

        result = (
            f"Weather in {city_name if city_name else weather.city}:\n"
            f"Description: {weather_desc}\n"
            f"Temperature: {temperature}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s\n"
        )
        
        self.result_text.insert(tk.END, result)