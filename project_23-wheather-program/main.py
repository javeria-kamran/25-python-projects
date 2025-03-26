import requests
import datetime
from pyfiglet import Figlet
from termcolor import colored
import geocoder
import json
import os
from collections import defaultdict

# ========== CONFIGURATION ==========
API_KEY = "2203925c7924239c97ac46a544442c31"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
HISTORY_FILE = "weather_history.json"
FAVORITES_FILE = "favorites.json"

# Weather icons mapping
WEATHER_ICONS = {
    "clear": "☀️", "clouds": "☁️", "rain": "🌧️", "drizzle": "🌦️",
    "thunderstorm": "⛈️", "snow": "❄️", "mist": "🌫️", "smoke": "💨",
    "haze": "🌫️", "dust": "💨", "fog": "🌁", "sand": "💨",
    "ash": "💨", "squall": "🌬️", "tornado": "🌪️"
}

# Color themes
THEMES = {
    "default": {
        "title": "cyan", "data": "white", "highlight": "yellow",
        "error": "red", "warning": "magenta"
    },
    "dark": {
        "title": "blue", "data": "light_grey", "highlight": "green",
        "error": "light_red", "warning": "light_magenta"
    },
    "light": {
        "title": "blue", "data": "black", "highlight": "red",
        "error": "red", "warning": "magenta"
    }
}

current_theme = "default"

# ========== UTILITY FUNCTIONS ==========
def get_theme_color(element):
    return THEMES[current_theme].get(element, "white")

def display_title():
    f = Figlet(font='slant')
    print(colored(f.renderText('Weather App'), get_theme_color("title")))
    print(colored("="*60, get_theme_color("title")))
    print()

def get_weather_icon(condition):
    condition = condition.lower()
    for key in WEATHER_ICONS:
        if key in condition:
            return WEATHER_ICONS[key]
    return "🌈"

def get_current_location():
    try:
        g = geocoder.ip('me')
        return g.city if g.city else None
    except Exception:
        return None

# ========== DATA MANAGEMENT ==========
def load_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                return defaultdict(int, history) if isinstance(history, dict) else defaultdict(int)
        return defaultdict(int)
    except Exception:
        return defaultdict(int)

def save_history(history):
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(dict(history), f)
    except Exception:
        pass

def load_favorites():
    try:
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, 'r') as f:
                favorites = json.load(f)
                return favorites if isinstance(favorites, list) else []
        return []
    except Exception:
        return []

def save_favorites(favorites):
    try:
        with open(FAVORITES_FILE, 'w') as f:
            json.dump(favorites, f)
    except Exception:
        pass

# ========== WEATHER FUNCTIONS ==========
def get_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
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
                "pressure": data["main"]["pressure"],
                "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
                "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S'),
                "coord": data["coord"]
            }
        return {"error": data.get("message", "City not found")}
    except Exception as e:
        return {"error": str(e)}

def display_weather(weather_data):
    if "error" in weather_data:
        print(colored(f"\nError: {weather_data['error']}", get_theme_color("error")))
        return
    
    icon = get_weather_icon(weather_data["condition"])
    print(colored("\n" + "="*60, get_theme_color("title")))
    print(colored(f"{icon} Current Weather in {weather_data['city']}, {weather_data['country']} {icon}", get_theme_color("title")))
    print(colored("="*60, get_theme_color("title")))
    
    print(colored(f"\n🌡️ Temperature: {weather_data['temperature']}°C", get_theme_color("data")))
    print(colored(f"   Feels like: {weather_data['feels_like']}°C", get_theme_color("data")))
    print(colored(f"\n{icon} Condition: {weather_data['condition']}", get_theme_color("data")))
    print(colored(f"\n💧 Humidity: {weather_data['humidity']}%", get_theme_color("data")))
    print(colored(f"\n🌬️ Wind: {weather_data['wind_speed']} m/s", get_theme_color("data")))
    print(colored(f"\n📊 Pressure: {weather_data['pressure']} hPa", get_theme_color("data")))
    print(colored(f"\n🌅 Sunrise: {weather_data['sunrise']}", get_theme_color("data")))
    print(colored(f"\n🌇 Sunset: {weather_data['sunset']}", get_theme_color("data")))
    print(colored("\n" + "="*60, get_theme_color("title")))

# ========== MENU FUNCTIONS ==========
def check_current_weather():
    city = input(colored("\nEnter city name (or leave blank for current location): ", get_theme_color("highlight")))
    
    if not city.strip():
        current_city = get_current_location()
        if current_city:
            city = current_city
        else:
            print(colored("\nCould not determine location. Please enter city name.", get_theme_color("error")))
            return
    
    weather_data = get_weather(city)
    display_weather(weather_data)
    
    if "error" not in weather_data:
        favorites = load_favorites()
        if city.lower() not in [f.lower() for f in favorites]:
            add = input(colored("\nAdd to favorites? (y/n): ", get_theme_color("highlight"))).lower()
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
    
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "cnt": days * 8  # 3-hour intervals for requested days
    }
    
    try:
        response = requests.get(FORECAST_URL, params=params, timeout=10)
        data = response.json()

        if response.status_code == 200:
            # Group forecast by day
            daily_forecast = defaultdict(list)
            for item in data["list"]:
                date = datetime.datetime.fromtimestamp(item["dt"]).strftime('%Y-%m-%d')
                daily_forecast[date].append({
                    "time": datetime.datetime.fromtimestamp(item["dt"]).strftime('%H:%M'),
                    "temp": round(item["main"]["temp"], 1),
                    "feels_like": round(item["main"]["feels_like"], 1),
                    "condition": item["weather"][0]["description"].title(),
                    "icon": get_weather_icon(item["weather"][0]["description"]),
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"],
                    "pop": f"{item.get('pop', 0) * 100:.0f}%"
                })
            
            # Display forecast
            print(colored("\n" + "=" * 60, get_theme_color("title")))
            print(colored(f"📅  {days}-Day Forecast for {city.title()}", get_theme_color("title")))
            print(colored("=" * 60, get_theme_color("title")))
            
            for date, forecasts in daily_forecast.items():
                date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
                print(colored(f"\n{date_obj.strftime('%A, %B %d, %Y')}", get_theme_color("highlight")))
                print(colored("-" * 40, get_theme_color("data")))
                
                for forecast in forecasts:
                    print(colored(f"\n🕒 {forecast['time']}: {forecast['icon']} {forecast['condition']}", get_theme_color("data")))
                    print(colored(f"   🌡️ Temp: {forecast['temp']}°C (Feels like {forecast['feels_like']}°C)", get_theme_color("data")))
                    print(colored(f"   💧 Humidity: {forecast['humidity']}%", get_theme_color("data")))
                    print(colored(f"   🌬️ Wind: {forecast['wind_speed']} m/s", get_theme_color("data")))
                    if forecast['pop'] != "0%":
                        print(colored(f"   ☔ Precipitation: {forecast['pop']} chance", get_theme_color("warning")))
            
            print(colored("\n" + "=" * 60, get_theme_color("title")))
        else:
            print(colored(f"\nError: {data.get('message', 'Forecast not available')}", get_theme_color("error")))
    except requests.exceptions.RequestException as e:
        print(colored(f"\nNetwork error: {str(e)}", get_theme_color("error")))
    except Exception as e:
        print(colored(f"\nAn error occurred: {str(e)}", get_theme_color("error")))

def view_history():
    history = load_history()
    if not history:
        print(colored("\nNo search history found.", get_theme_color("warning")))
        return
    
    print(colored("\nSearch History:", get_theme_color("title")))
    for city, count in sorted(history.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(colored(f"- {city.title()}: {count} searches", get_theme_color("data")))

def manage_favorites():
    favorites = load_favorites()
    
    while True:
        print(colored("\nFavorite Cities:", get_theme_color("title")))
        for i, city in enumerate(favorites, 1):
            print(colored(f"{i}. {city}", get_theme_color("data")))
        
        print(colored("\n1. Add city", get_theme_color("highlight")))
        print(colored("2. Remove city", get_theme_color("highlight")))
        print(colored("3. Back", get_theme_color("highlight")))
        
        choice = input(colored("\nChoose option: ", get_theme_color("highlight")))
        
        if choice == "1":
            city = input(colored("Enter city name: ", get_theme_color("highlight")))
            if city and city.lower() not in [f.lower() for f in favorites]:
                favorites.append(city)
                save_favorites(favorites)
        elif choice == "2" and favorites:
            try:
                idx = int(input(colored("Enter number to remove: ", get_theme_color("highlight")))) - 1
                if 0 <= idx < len(favorites):
                    favorites.pop(idx)
                    save_favorites(favorites)
            except ValueError:
                pass
        elif choice == "3":
            break

def change_theme():
    global current_theme
    print(colored("\nAvailable themes:", get_theme_color("title")))
    for i, theme in enumerate(THEMES.keys(), 1):
        print(colored(f"{i}. {theme.capitalize()}", get_theme_color("data")))
    
    try:
        choice = int(input(colored("\nSelect theme: ", get_theme_color("highlight"))))
        if 1 <= choice <= len(THEMES):
            current_theme = list(THEMES.keys())[choice-1]
            print(colored(f"\nTheme changed to {current_theme}!", get_theme_color("highlight")))
    except ValueError:
        pass

# ========== MAIN FUNCTION ==========
def main():
    # Initialize files
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w') as f:
            json.dump({}, f)
    if not os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'w') as f:
            json.dump([], f)
    
    display_title()
    
    # Test API
    test_data = get_weather("London")
    if "error" in test_data:
        print(colored("\nAPI Error: " + test_data["error"], get_theme_color("error")))
    
    while True:
        print(colored("\nMain Menu", get_theme_color("title")))
        print(colored("1. Current Weather", get_theme_color("data")))
        print(colored("2. Weather Forecast", get_theme_color("data")))
        print(colored("3. View History", get_theme_color("data")))
        print(colored("4. Manage Favorites", get_theme_color("data")))
        print(colored("5. Change Theme", get_theme_color("data")))
        print(colored("6. Exit", get_theme_color("data")))
        
        choice = input(colored("\nEnter choice (1-6): ", get_theme_color("highlight")))
        
        if choice == "1":
            check_current_weather()
        elif choice == "2":
            check_forecast()
        elif choice == "3":
            view_history()
        elif choice == "4":
            manage_favorites()
        elif choice == "5":
            change_theme()
        elif choice == "6":
            print(colored("\nGoodbye!", get_theme_color("title")))
            break

if __name__ == "__main__":
    main()