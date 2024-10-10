import requests
import tkinter as tk
from tkinter import messagebox, Listbox, StringVar, Text, Scrollbar
import urllib.parse  # TEMP

from config import *
from src.weather import get_weather_man, Weather, WeatherMan, WeatherDay

class WeatherApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Weather App")
        self.master.geometry("800x1300")

        # Add your name
        self.name_label = tk.Label(master, text="Baylus Tunnicliff", font=("Arial", 12, "bold"))
        self.name_label.pack(pady=10)

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
        
        self.location_button = tk.Button(master, text="Use Current Location", command=self.use_current_location)
        self.location_button.pack(pady=10)

        self.result_text = tk.Text(master, height=8, width=50)
        self.result_text.pack(pady=10)

        self.city_data = []  # To store city suggestions
        self.debounce_timer = None  # To store the timer reference

        # Forecast
        self.forecast_frame = tk.Frame(master)
        self.forecast_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.forecast_text = Text(self.forecast_frame, height=15, width=50)
        self.forecast_text.pack(fill=tk.BOTH, expand=True)
        
        # Frame for forecast buttons
        self.forecast_button_frame = tk.Frame(master)
        self.forecast_button_frame.pack(pady=10, fill=tk.X)

        # Frame for hourly details
        self.hourly_frame = tk.Frame(master)
        self.hourly_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.hourly_text = tk.Text(self.hourly_frame, height=15, width=50)
        self.hourly_text.pack(fill=tk.BOTH, expand=True)
        
        # Add Info Button
        self.info_button = tk.Button(master, text="Info", command=self.show_info)
        self.info_button.pack(pady=10)

    def debounce_suggestions(self, event=None):
        if self.debounce_timer is not None:
            self.master.after_cancel(self.debounce_timer)  # Cancel the previous timer
        
        # Set a new timer
        self.debounce_timer = self.master.after(1000, self.get_suggestions)  # 1000ms debounce time

    def get_current_location(self):
        try:
            response = requests.get('http://ipinfo.io/json')
            data = response.json()
            loc = data['loc'].split(',')
            city = data['city']
            state = data['region']
            country = data['country']
            return f"{city}, {state}, {country}"
        except Exception as e:
            messagebox.showerror("Error", f"Could not determine location: {e}")
            return None

    def use_current_location(self):
        current_location = self.get_current_location()
        if current_location:
            self.city_var.set(current_location)
            self.get_weather()

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
            self.city_var.set(f"{city_name}, {state}, {country}" if state else f"{city_name}, {country}")
            self.suggestions_box.delete(0, tk.END)  # Clear suggestions

    def get_weather(self):
        city = self.city_var.get()
        try:
            weatherman: WeatherMan = get_weather_man(city)
            weatherman.fetch_forecast()
        except Exception as e:
            messagebox.showerror("Error", f"City not found: {e}")
        
        self.display_weather(weatherman.current_weather, city)
        self.display_forecast(weatherman.forecast)

    def display_weather(self, weather: Weather, city_name: str = ""):
        self.result_text.delete(1.0, tk.END)  # Clear previous results
        weather_desc = weather.weather_description
        temperature = weather.temperature
        humidity = weather.humidity
        wind_speed = weather.wind_speed

        result = (
            f"Weather in {city_name if city_name else 'Unknown'}:\n"
            f"Description: {weather_desc}\n"
            f"Temperature: {temperature}°F\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} m/s\n"
        )
        
        self.result_text.insert(tk.END, result)

    def display_forecast(self, forecast: list[WeatherDay]):
        self.forecast_text.delete(1.0, tk.END)
        # Clear previous buttons and hourly details
        for widget in self.forecast_button_frame.winfo_children():
            widget.destroy()
        self.hourly_text.delete(1.0, tk.END)

        self.forecast_days = forecast  # Store the forecast days
        result = "5-Day Forecast:"
        for idx, entry in enumerate(forecast):
            date_str = entry.weather_objects[0].timestamp.split(" ")[0]  # Get the date from the first Weather object
            average_humidity, average_wind_speed, common_description = entry.calculate_averages()
            result += (
                f"\n\n{date_str}:\n"
                f"  High: {entry.temp_high}°F\n"
                f"  Low: {entry.temp_low}°F\n"
                f"  Avg Humidity: {average_humidity:.2f}%\n"
                f"  Avg Wind Speed: {average_wind_speed:.2f} m/s\n"
                f"  Most Common Weather: {common_description}"
            )
            date_str = entry.weather_objects[0].timestamp.split(" ")[0]
            button = tk.Button(self.forecast_button_frame, text=date_str, 
                               command=lambda day=idx: self.show_hourly_details(day))
            button.pack(side=tk.LEFT, padx=5)
        
        self.forecast_text.insert(tk.END, result)

    def show_hourly_details(self, day_index):
        self.hourly_text.delete(1.0, tk.END)  # Clear previous hourly details
        hourly_data = self.get_hourly_data(day_index)  # Fetch hourly data for the selected day
        
        # Display hourly details
        for hour in hourly_data:
            self.hourly_text.insert(tk.END, hour + "\n")

    def get_hourly_data(self, day_index):
        """Retrieve hourly data for the given day index."""
        if 0 <= day_index < len(self.forecast_days):
            day = self.forecast_days[day_index]
            hourly_details = []
            for weather in day.weather_objects:
                hour_info = (
                    f"Time: {weather.timestamp} | "
                    f"Temperature: {weather.temperature}°F | "
                    f"Description: {weather.weather_description} | "
                    f"Humidity: {weather.humidity}% | "
                    f"Wind Speed: {weather.wind_speed} m/s"
                )
                hourly_details.append(hour_info)
            return hourly_details
        return []

    def show_info(self):
        info_text = (
            "PM Accelerator: Hiring and getting hired for product management roles is hard. "
            "In the short timeframe of an interview, it is difficult to precisely assess and display "
            "the necessary, complex skills.\n\n"
            "Product Managers play key roles in a company. Hiring for those positions shouldn’t be a guessing game.\n\n"
            "It is our vision, to make it simple and beneficial for Product Managers to accurately display their skills "
            "and empower hiring companies to choose the right Product Manager every time."
        )
        messagebox.showinfo("Information", info_text)