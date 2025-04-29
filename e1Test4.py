import ee
import geemap
import webbrowser
import datetime

# Autenticación e inicialización
ee.Authenticate()
ee.Initialize(project='light-sunup-288723')  # Usa tu ID si es diferente

#Selección de coordenadas de interés
lat = float(input("COORDENADAS DE LATITUD: "))
long = float(input("COORDENADAS DE LONGITUD: "))

#Creación de punto geométrico
punto = ee.Geometry.Point([long,lat])
area = punto.buffer(30)

#Definición de fecha
hoy = datetime.date.today()
#inicio = ee.Date(str(hoy - datetime.timedelta(days=7)))
#fin = ee.Date(str(hoy))
#Debido a que algunas bases de datos tienen retraso de unas semanas, se van a usar las siguientes fechas
inicio = '2025-03-01'
fin = '2025-04-07'

#Importar datos de NDVI
# MODIS/061/MOD13Q1 --> Base de datos de NDVI con cadencia de 16 días
ndvi = ee.ImageCollection('MODIS/061/MOD13Q1').filterDate(inicio,fin).select('NDVI').mean().clip(area)

#Importar datos de Temperatura de Superficie Terrestre
#MODIS/061/MOD11A2 --> Base de dasos de Temperatura de Superficie Terrestre con cadencia de 8 días
lst_collection = ee.ImageCollection('MODIS/061/MOD11A2').filterDate(inicio,fin).select('LST_Day_1km')

#print('Número de imágenes LST:', lst_collection.size().getInfo())
#Promedio de lst y conversión a °C
lst_image = lst_collection.mean().multiply(0.02).subtract(273.15).rename('Temperatura_C').clip(area)

#Importar datos de Velocidad del Viento
#NOAA/GFS0P25 --> GFS: Global Forecast System Predicted Atmosphere Data con cadencia de 6 horas
wind_collection = ee.ImageCollection('NOAA/GFS0P25').filterDate(inicio,fin).select(['u_component_of_wind_10m_above_ground','v_component_of_wind_10m_above_ground'])

#Media de componentes U & V
meanU = wind_collection.select('u_component_of_wind_10m_above_ground').mean()
meanV = wind_collection.select('v_component_of_wind_10m_above_ground').mean()

#Cálculo de magnitud del viendo y renombre de variable
wind_speed = meanU.hypot(meanV).rename('WindSpeed_m/s').clip(area)

#Importar datos de Pendiente
dem = ee.Image('USGS/SRTMGL1_003')
slope = ee.Terrain.slope(dem).rename('Pendiente_Angulo').clip(area)

#Combinamos en una sola imagen
imagen_completa = ndvi.rename('NDVI').addBands(lst_image).addBands(wind_speed).addBands(slope)

#Muestreo de datos dentro del Buffer
muestreo = imagen_completa.sample(region=area,scale=1,numPixels=100,geometries=True)

#Lo Convertimos a un diccionario
datos = muestreo.getInfo()

#Mostramos los resultados
for feature in datos['features']:
    props = feature['properties']
    coords = feature['geometry']['coordinates']
    print(f"Lat: {coords[1]}, Long: {coords[0]} | NDVI: {props['NDVI']}, Temp: {props['Temperatura_C']} °C, Viento: {props['WindSpeed_m/s']} m/s, Pendiente: {props['Pendiente_Angulo']}°")
