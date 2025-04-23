from Api_file import get_weather_data
from Api_file import get_ndvi
from Api_file import get_slope
from computingFWI import calculate_fwi

# Coordenadas que se obtendran de ardupilot
lat = 25.6866
lon = -100.3161
api_key = 'd73f8f737d7728a9d2ea0ffcd8779ff2' #API OpenWeather
MAPBOX_TOKEN = 'pk.eyJ1IjoiamFjb2JvMjciLCJhIjoiY204eW5maTdjMDMwODJqb293ZGd4cTNscSJ9.0_kcUB4XbYyrw3PPGT-QuQ'
ZOOM = 15  # Quieres mayor o menor resolución

# Obtener datos del clima
row = get_weather_data(lat, lon, api_key)

# Calcular FWI
indices = calculate_fwi(row)

#Calcular NDVI
ndvi = get_ndvi(lat,lon)

#Calcular slope
slope = get_slope(lat, lon, ZOOM, MAPBOX_TOKEN)

# Mostrar resultados
print("\n📊 Resultados FWI:")
for key, value in indices.items():
    print(f"{key}: {value:.2f}")

print("\n NDVI:")
print("\n",ndvi)

print("\n Slope:")
print("\n",slope)

#calcular riesgo de incendio

risk = 0.3*indices['BUI']+0.3*ndvi+0.4*slope
print("\n Riesgo de incendio:")
print("\n",risk)