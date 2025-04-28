from Api_file import get_weather_data
from Api_file import get_ndvi
from Api_file import get_slope
from computingFWI import calculate_fwi
from coordinates import get_coordinates
from risk_score import calculate_risk_score

# Coordenadas que se obtendran de ardupilot
lat,lon = 25.618611, -100.356977 #get_coordinates()

#calorimetria
T = 30 # Temperatura de la coordenada a evaluar
T_norm = (T+10)/(140+10) # Normalización de la temperatura máxima

# Obtener datos del clima
row = get_weather_data(lat, lon)

# Calcular FWI
indices = calculate_fwi(row)

#Calcular NDVI
ndvi = get_ndvi(lat,lon)

#Calcular slope
slope = get_slope(lat, lon)

# Mostrar resultados
print("\n📊 Resultados FWI:")
for key, value in indices.items():
    print(f"{key}: {value:.2f}")

print("\n NDVI:")
print("\n",ndvi)

print("\n Slope:")
print("\n",slope)

#calcular riesgo de incendio
risk = calculate_risk_score(indices, ndvi, slope, T_norm)
print(f"\n🔥 Risk Score: {risk:.2f}")