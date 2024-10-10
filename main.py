"""
Retrieve weather details for a given city.
"""
import tkinter as tk

from src.gui import WeatherApp


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()