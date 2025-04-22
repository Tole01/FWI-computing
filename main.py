from Api_file import get_weather_data
from computingFWI import calculate_fwi

# Coordenadas y API key
lat = 25.6866
lon = -100.3161
api_key = 'd73f8f737d7728a9d2ea0ffcd8779ff2'

# Obtener datos del clima
row = get_weather_data(lat, lon, api_key)

# Calcular FWI
indices = calculate_fwi(row)

# Mostrar resultados
print("\n📊 Resultados FWI:")
for key, value in indices.items():
    print(f"{key}: {value:.2f}")
