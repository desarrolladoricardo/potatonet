import requests
from bs4 import BeautifulSoup
import datetime

def get_weather_data(city="Tunja"):
    """
    Fetches weather data from Open-Meteo API (Free, No Key).
    Returns a dictionary with temperature, text description, and humidity.
    """
    try:
        # Coordinates for Open-Meteo
        coords = {
            "Tunja": {"lat": 5.5353, "lon": -73.3678},
            "Bogota": {"lat": 4.7110, "lon": -74.0721}
        }
        
        target = coords.get(city, coords["Tunja"])
        
        # WMO Weather interpretation codes (WW)
        wmo_codes = {
            0: "Cielo despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
            45: "Niebla", 48: "Niebla con escarcha",
            51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna densa",
            61: "Lluvia leve", 63: "Lluvia moderada", 65: "Lluvia fuerte",
            80: "Chubascos leves", 81: "Chubascos moderados", 82: "Chubascos violentos",
            95: "Tormenta eléctrica"
        }

        url = f"https://api.open-meteo.com/v1/forecast?latitude={target['lat']}&longitude={target['lon']}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code&timezone=America%2FBogota"
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        current = data['current']
        weather_code = current['weather_code']
        description = wmo_codes.get(weather_code, "Variable")
        
        return {
            'temp_C': current['temperature_2m'],
            'desc': description,
            'humidity': current['relative_humidity_2m'],
            'feels_like': current['apparent_temperature'],
            'city': city
        }
    except Exception as e:
        print(f"Error fetching weather for {city}: {e}")
        return {
            'temp_C': "--",
            'desc': "No disponible",
            'humidity': "--",
            'feels_like': "--",
            'city': city
        }

def get_moon_phase():
    """
    Fetches moon phase data from wttr.in (astronomy section).
    """
    try:
        url = "https://wttr.in/Tunja?format=j1&lang=es"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Astronomy data is in weather -> astronomy
        astronomy = data['weather'][0]['astronomy'][0]
        
        raw_phase = astronomy['moon_phase']
        
        # Translation Dictionary
        translations = {
            "New Moon": "Luna Nueva",
            "Waxing Crescent": "Luna Creciente",
            "First Quarter": "Cuarto Creciente",
            "Waxing Gibbous": "Gibosa Creciente",
            "Full Moon": "Luna Llena",
            "Waning Gibbous": "Gibosa Menguante",
            "Last Quarter": "Cuarto Menguante",
            "Waning Crescent": "Luna Menguante"
        }
        
        phase_es = translations.get(raw_phase, raw_phase)
        
        return {
            'phase': phase_es,
            'illumination': astronomy['moon_illumination'],
            'moonrise': astronomy['moonrise'],
            'moonset': astronomy['moonset']
        }
    except Exception as e:
        print(f"Error fetching moon phase: {e}")
        return {
            'phase': "Desconocida",
            'illumination': "--",
            'moonrise': "--",
            'moonset': "--"
        }

def get_dollar_trm():
    """
    Fetches the Dollar TRM from Datos Abiertos Colombia (JSON API).
    Fallback to simple scraping if API fails.
    """
    try:
        # Datos.gov.co Socrata API for TRM
        # This dataset endpoint is usually reliable for everyday TRM
        url = "https://www.datos.gov.co/resource/32sa-8pi3.json?$limit=1&$order=vigenciahasta%20DESC"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data:
            trm = float(data[0]['valor'])
            return f"${trm:,.2f}"
    except Exception as e:
        print(f"Error fetching TRM from API, trying scraping: {e}")
    
    # Fallback Scraping (Dolar Colombia)
    try:
        url = "https://dolar.wilkinsonpc.com.co/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        # This selector might need adjustment depending on the site structure
        price_div = soup.find('div', {'class': 'numero'})
        if price_div:
            return price_div.text.strip()
    except Exception as e:
        print(f"Error scraping dollar: {e}")
    
    return "No disponible"

if __name__ == "__main__":
    print("Testing Scraper...")
    print("Weather:", get_weather_data())
    print("Moon:", get_moon_phase())
    print("Dollar:", get_dollar_trm())
