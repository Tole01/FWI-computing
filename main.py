from Api_file import get_weather_data
from computingFWI import calculate_fwi

# Coordenadas y API key
lat = 19.4326
lon = -99.1332
api_key = 'd73f8f737d7728a9d2ea0ffcd8779ff2'

# Obtener datos del clima
row = get_weather_data(lat, lon, api_key)

# Calcular FWI
indices = calculate_fwi(row)

# Mostrar resultados
print("\n📊 Resultados FWI:")
for key, value in indices.items():
    print(f"{key}: {value:.2f}")
