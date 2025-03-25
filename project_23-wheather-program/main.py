import requests
import datetime
from pyfiglet import Figlet
from termcolor import colored
import geocoder
import time
import json
import os
from collections import defaultdict

# Configuration
API_KEY = "2203925c7924239c97ac46a544442c31"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
HISTORY_FILE = "weather_history.json"
FAVORITES_FILE = "favorites.json"

# Weather icons mapping
WEATHER_ICONS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "drizzle": "🌦️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "smoke": "💨",
    "haze": "🌫️",
    "dust": "💨",
    "fog": "🌁",
    "sand": "💨",
    "ash": "💨",
    "squall": "🌬️",
    "tornado": "🌪️"
}

# Color themes
THEMES = {
    "default": {
        "title": "cyan",
        "data": "white",
        "highlight": "yellow",
        "error": "red",
        "warning": "magenta"
    },
    "dark": {
        "title": "blue",
        "data": "light_grey",
        "highlight": "green",
        "error": "light_red",
        "warning": "light_magenta"
    },
    "light": {
        "title": "blue",
        "data": "black",
        "highlight": "red",
        "error": "red",
        "warning": "magenta"
    }
}

current_theme = "default"

def display_title():
    """Display a fancy title for the app"""
    f = Figlet(font='slant')
    print(colored(f.renderText('Weather App'), "cyan"), colored("by Awesome Dev", "magenta"))
    print(colored("=" * 60, "cyan"))
    print()

def get_theme_color(element):
    """Get color for UI element based on current theme"""
    return THEMES[current_theme].get(element, "white")

def get_weather_icon(condition):
    """Get appropriate weather icon for the condition"""
    condition = condition.lower()
    for key in WEATHER_ICONS:
        if key in condition:
            return WEATHER_ICONS[key]
    return "🌈"

def get_current_location():
    """Try to get current location using geocoder"""
    try:
        g = geocoder.ip('me')
        if g.city:
            return g.city
        return None
    except Exception:
        return None

def load_history():
    """Load search history from file"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        return defaultdict(int)
    return defaultdict(int)

def save_history(history):
    """Save search history to file"""
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception:
        pass

def load_favorites():
    """Load favorite cities from file"""
    try:
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        return []
    return []

def save_favorites(favorites):
    """Save favorite cities to file"""
    try:
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(favorites, f)
    except Exception:
        pass

def get_weather(city):
    """Get current weather data for a city"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()

        if data.get("cod") == 200:
            # Add to search history
            history = load_history()
            history[city.lower()] += 1
            save_history(history)
            
            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": round(data["main"]["temp"], 1),
                "feels_like": round(data["main"]["feels_like"], 1),
                "condition": data["weather"][0]["description"].title(),
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", "N/A"),
                "pressure": data["main"]["pressure"],
                "visibility": data.get("visibility", "N/A"),
                "clouds": data["clouds"]["all"],
                "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
                "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S'),
                "timezone": data["timezone"],
                "coord": data["coord"],
                "timestamp": datetime.datetime.fromtimestamp(data["dt"]).strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {"error": data.get("message", "City not found!")}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def get_forecast(city, days=3):
    """Get weather forecast for a city"""
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": days * 8  # 3-hour intervals for 5 days max (API limit)
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        data = response.json()

        if data.get("cod") == "200":
            forecast = []
            for item in data["list"]:
                forecast.append({
                    "datetime": datetime.datetime.fromtimestamp(item["dt"]).strftime('%Y-%m-%d %H:%M'),
                    "temperature": round(item["main"]["temp"], 1),
                    "feels_like": round(item["main"]["feels_like"], 1),
                    "condition": item["weather"][0]["description"].title(),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "pop": item.get("pop", 0) * 100  # Probability of precipitation
                })
            return forecast
        else:
            return {"error": data.get("message", "Forecast data not available")}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def get_air_quality(lat, lon):
    """Get air quality data for coordinates"""
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY
    }
    
    try:
        response = requests.get(AIR_QUALITY_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("cod") is None:  # Successful response doesn't have 'cod'
            aqi = data["list"][0]["main"]["aqi"]
            components = data["list"][0]["components"]
            
            # AQI description
            aqi_levels = {
                1: "Good",
                2: "Fair",
                3: "Moderate",
                4: "Poor",
                5: "Very Poor"
            }
            
            return {
                "aqi": aqi,
                "aqi_description": aqi_levels.get(aqi, "Unknown"),
                "components": components
            }
        else:
            return {"error": data.get("message", "Air quality data not available")}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def display_weather(weather_data):
    """Display weather information in a formatted way"""
    if "error" in weather_data:
        print(colored(f"\nError: {weather_data['error']}", get_theme_color("error")))
        return
    
    icon = get_weather_icon(weather_data["condition"])
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))
    print(colored(f"{icon}  Current Weather in {weather_data['city']}, {weather_data['country']}  {icon}", get_theme_color("title")))
    print(colored("=" * 60, get_theme_color("title")))
    
    print(colored(f"\n🌡️ Temperature: ", get_theme_color("data")) + 
          colored(f"{weather_data['temperature']}°C", get_theme_color("highlight")) + 
          colored(f" (Feels like {weather_data['feels_like']}°C)", get_theme_color("data")))
    
    print(colored(f"\n{get_weather_icon(weather_data['condition'])} Condition: ", get_theme_color("data")) + 
          colored(weather_data['condition'], get_theme_color("highlight")))
    
    print(colored("\n💧 Humidity: ", get_theme_color("data")) + 
          colored(f"{weather_data['humidity']}%", get_theme_color("highlight")))
    
    print(colored("\n🌬️ Wind: ", get_theme_color("data")) + 
          colored(f"{weather_data['wind_speed']} m/s", get_theme_color("highlight")))
    
    if weather_data['wind_direction'] != "N/A":
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        idx = round(weather_data['wind_direction'] / 45) % 8
        print(colored("   Direction: ", get_theme_color("data")) + 
              colored(f"{directions[idx]} ({weather_data['wind_direction']}°)", get_theme_color("highlight")))
    
    print(colored("\n☁️ Clouds: ", get_theme_color("data")) + 
          colored(f"{weather_data['clouds']}%", get_theme_color("highlight")))
    
    print(colored("\n📊 Pressure: ", get_theme_color("data")) + 
          colored(f"{weather_data['pressure']} hPa", get_theme_color("highlight")))
    
    if weather_data['visibility'] != "N/A":
        print(colored("\n👁️ Visibility: ", get_theme_color("data")) + 
              colored(f"{weather_data['visibility'] / 1000} km", get_theme_color("highlight")))
    
    print(colored("\n🌅 Sunrise: ", get_theme_color("data")) + 
          colored(weather_data['sunrise'], get_theme_color("highlight")))
    
    print(colored("\n🌇 Sunset: ", get_theme_color("data")) + 
          colored(weather_data['sunset'], get_theme_color("highlight")))
    
    print(colored("\n🕒 Last Updated: ", get_theme_color("data")) + 
          colored(weather_data['timestamp'], get_theme_color("highlight")))
    
    # Get and display air quality
    aq_data = get_air_quality(weather_data['coord']['lat'], weather_data['coord']['lon'])
    if "error" not in aq_data:
        print(colored("\n🍃 Air Quality Index (AQI): ", get_theme_color("data")) + 
              colored(f"{aq_data['aqi']} - {aq_data['aqi_description']}", get_theme_color("highlight")))
        
        print(colored("\n   Pollutants:", get_theme_color("data")))
        for pol, val in aq_data['components'].items():
            print(colored(f"   - {pol.upper()}: ", get_theme_color("data")) + 
                  colored(f"{val} μg/m³", get_theme_color("highlight")))
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))

def display_forecast(forecast_data):
    """Display weather forecast in a formatted way"""
    if "error" in forecast_data:
        print(colored(f"\nError: {forecast_data['error']}", get_theme_color("error")))
        return
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))
    print(colored("📅  Weather Forecast  📅", get_theme_color("title")))
    print(colored("=" * 60, get_theme_color("title")))
    
    # Group by day
    daily_forecast = defaultdict(list)
    for item in forecast_data:
        date = item['datetime'].split()[0]
        daily_forecast[date].append(item)
    
    for date, items in daily_forecast.items():
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        print(colored(f"\n{date_obj.strftime('%A, %B %d, %Y')}", get_theme_color("highlight")))
        print(colored("-" * 40, get_theme_color("data")))
        
        for item in items:
            time = item['datetime'].split()[1][:5]
            icon = get_weather_icon(item['condition'])
            
            print(colored(f"\n🕒 {time}: ", get_theme_color("data")) + 
                  colored(f"{icon} {item['condition']}", get_theme_color("highlight")))
            
            print(colored("   🌡️ Temp: ", get_theme_color("data")) + 
                  colored(f"{item['temperature']}°C (Feels like {item['feels_like']}°C)", get_theme_color("highlight")))
            
            print(colored("   💧 Humidity: ", get_theme_color("data")) + 
                  colored(f"{item['humidity']}%", get_theme_color("highlight")))
            
            print(colored("   🌬️ Wind: ", get_theme_color("data")) + 
                  colored(f"{item['wind_speed']} m/s", get_theme_color("highlight")))
            
            if item['pop'] > 0:
                print(colored("   ☔ Precipitation: ", get_theme_color("data")) + 
                      colored(f"{item['pop']}% chance", get_theme_color("warning")))
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))

def display_history():
    """Display search history"""
    history = load_history()
    if not history:
        print(colored("\nNo search history found.", get_theme_color("warning")))
        return
    
    sorted_history = sorted(history.items(), key=lambda x: x[1], reverse=True)
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))
    print(colored("🔍 Search History (by frequency)", get_theme_color("title")))
    print(colored("=" * 60, get_theme_color("title")))
    
    for idx, (city, count) in enumerate(sorted_history[:10], 1):  # Show top 10
        print(colored(f"\n{idx}. {city.title()}: ", get_theme_color("data")) + 
              colored(f"{count} searches", get_theme_color("highlight")))

def display_favorites():
    """Display favorite cities"""
    favorites = load_favorites()
    if not favorites:
        print(colored("\nNo favorite cities saved.", get_theme_color("warning")))
        return
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))
    print(colored("❤️ Favorite Cities", get_theme_color("title")))
    print(colored("=" * 60, get_theme_color("title")))
    
    for idx, city in enumerate(favorites, 1):
        print(colored(f"\n{idx}. {city}", get_theme_color("data")))

def main_menu():
    """Display main menu and handle user input"""
    while True:
        print(colored("\n" + "=" * 60, get_theme_color("title")))
        print(colored("Main Menu", get_theme_color("title")))
        print(colored("=" * 60, get_theme_color("title")))
        
        print(colored("\n1. Check current weather", get_theme_color("data")))
        print(colored("2. Check weather forecast", get_theme_color("data")))
        print(colored("3. View search history", get_theme_color("data")))
        print(colored("4. Manage favorite cities", get_theme_color("data")))
        print(colored("5. Change theme", get_theme_color("data")))
        print(colored("6. Exit", get_theme_color("data")))
        
        choice = input(colored("\nEnter your choice (1-6): ", get_theme_color("highlight")))
        
        if choice == "1":
            check_current_weather()
        elif choice == "2":
            check_forecast()
        elif choice == "3":
            display_history()
        elif choice == "4":
            manage_favorites()
        elif choice == "5":
            change_theme()
        elif choice == "6":
            print(colored("\nGoodbye! Have a nice day! 🌈", get_theme_color("title")))
            break
        else:
            print(colored("\nInvalid choice. Please try again.", get_theme_color("error")))

def check_current_weather():
    """Handle current weather checking"""
    city = input(colored("\nEnter city name (or leave blank for current location): ", get_theme_color("highlight")))
    
    if not city.strip():
        current_city = get_current_location()
        if current_city:
            print(colored(f"\nUsing your current location: {current_city}", get_theme_color("data")))
            city = current_city
        else:
            print(colored("\nCould not determine current location. Please enter a city name.", get_theme_color("error")))
            return
    
    weather_data = get_weather(city)
    display_weather(weather_data)
    
    if "error" not in weather_data:
        # Add to favorites prompt
        favorites = load_favorites()
        if city.lower() not in [f.lower() for f in favorites]:
            add = input(colored("\nAdd this city to favorites? (y/n): ", get_theme_color("highlight"))).lower()
            if add == 'y':
                favorites.append(city)
                save_favorites(favorites)
                print(colored(f"\n{city} added to favorites!", get_theme_color("highlight")))

def check_forecast():
    """Handle weather forecast checking"""
    city = input(colored("\nEnter city name (or leave blank for current location): ", get_theme_color("highlight")))
    
    if not city.strip():
        current_city = get_current_location()
        if current_city:
            print(colored(f"\nUsing your current location: {current_city}", get_theme_color("data")))
            city = current_city
        else:
            print(colored("\nCould not determine current location. Please enter a city name.", get_theme_color("error")))
            return
    
    days = input(colored("\nEnter number of days to forecast (1-5, default 3): ", get_theme_color("highlight")))
    try:
        days = min(max(int(days), 1), 5) if days.strip() else 3
    except ValueError:
        days = 3
        print(colored("\nInvalid input. Using default 3 days.", get_theme_color("warning")))
    
    forecast_data = get_forecast(city, days)
    display_forecast(forecast_data)

def manage_favorites():
    """Handle favorite cities management"""
    favorites = load_favorites()
    
    while True:
        print(colored("\n" + "=" * 60, get_theme_color("title")))
        print(colored("Manage Favorite Cities", get_theme_color("title")))
        print(colored("=" * 60, get_theme_color("title")))
        
        print(colored("\n1. View favorite cities", get_theme_color("data")))
        print(colored("2. Add a city to favorites", get_theme_color("data")))
        print(colored("3. Remove a city from favorites", get_theme_color("data")))
        print(colored("4. Check weather for a favorite city", get_theme_color("data")))
        print(colored("5. Back to main menu", get_theme_color("data")))
        
        choice = input(colored("\nEnter your choice (1-5): ", get_theme_color("highlight")))
        
        if choice == "1":
            display_favorites()
        elif choice == "2":
            city = input(colored("\nEnter city name to add: ", get_theme_color("highlight"))).strip()
            if city:
                if city.lower() not in [f.lower() for f in favorites]:
                    favorites.append(city)
                    save_favorites(favorites)
                    print(colored(f"\n{city} added to favorites!", get_theme_color("highlight")))
                else:
                    print(colored(f"\n{city} is already in favorites.", get_theme_color("warning")))
            else:
                print(colored("\nCity name cannot be empty.", get_theme_color("error")))
        elif choice == "3":
            if not favorites:
                print(colored("\nNo favorite cities to remove.", get_theme_color("warning")))
                continue
                
            display_favorites()
            try:
                idx = int(input(colored("\nEnter number of city to remove: ", get_theme_color("highlight")))) - 1
                if 0 <= idx < len(favorites):
                    removed = favorites.pop(idx)
                    save_favorites(favorites)
                    print(colored(f"\n{removed} removed from favorites.", get_theme_color("highlight")))
                else:
                    print(colored("\nInvalid selection.", get_theme_color("error")))
            except ValueError:
                print(colored("\nPlease enter a valid number.", get_theme_color("error")))
        elif choice == "4":
            if not favorites:
                print(colored("\nNo favorite cities saved.", get_theme_color("warning")))
                continue
                
            display_favorites()
            try:
                idx = int(input(colored("\nEnter number of city to check: ", get_theme_color("highlight")))) - 1
                if 0 <= idx < len(favorites):
                    weather_data = get_weather(favorites[idx])
                    display_weather(weather_data)
                else:
                    print(colored("\nInvalid selection.", get_theme_color("error")))
            except ValueError:
                print(colored("\nPlease enter a valid number.", get_theme_color("error")))
        elif choice == "5":
            break
        else:
            print(colored("\nInvalid choice. Please try again.", get_theme_color("error")))

def change_theme():
    """Change the color theme of the application"""
    global current_theme
    
    print(colored("\n" + "=" * 60, get_theme_color("title")))
    print(colored("Change Theme", get_theme_color("title")))
    print(colored("=" * 60, get_theme_color("title")))
    
    print(colored("\nAvailable themes:", get_theme_color("data")))
    for idx, theme in enumerate(THEMES.keys(), 1):
        print(colored(f"{idx}. {theme.capitalize()}", get_theme_color("highlight")))
    
    choice = input(colored("\nEnter theme number: ", get_theme_color("highlight")))
    try:
        theme_idx = int(choice) - 1
        if 0 <= theme_idx < len(THEMES):
            current_theme = list(THEMES.keys())[theme_idx]
            print(colored(f"\nTheme changed to {current_theme.capitalize()}!", get_theme_color("highlight")))
        else:
            print(colored("\nInvalid theme selection.", get_theme_color("error")))
    except ValueError:
        print(colored("\nPlease enter a valid number.", get_theme_color("error")))

def main():
    """Main function to run the weather app"""
    display_title()
    
    # Check if API is working
    test_data = get_weather("London")
    if "error" in test_data and "Invalid API key" in test_data["error"]:
        print(colored("\nERROR: Invalid API key. Please check your OpenWeatherMap API key.", get_theme_color("error")))
        return
    
    print(colored("Welcome to Awesome Weather App!", get_theme_color("title")))
    print(colored("Getting weather information from OpenWeatherMap...", get_theme_color("data")))
    
    main_menu()

if __name__ == "__main__":
    main()