import requests
import datetime

def get_weather_data(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    data = requests.get(url).json()

    temperatura = data['main']['temp']
    humedad = data['main']['humidity']
    viento_m_s = data['wind']['speed']
    precipitacion = data.get('rain', {}).get('1h', 0.0)
    viento_kmh = viento_m_s * 3.6
    mes = datetime.datetime.now().month

    return {
        't2m_C': temperatura,
        'humedad_relativa': humedad,
        'wind_speed_kmh': viento_kmh,
        'precipitation_mm': precipitacion,
        'month': mes
    }
