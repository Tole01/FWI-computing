import ee
import random
from datetime import timedelta

# Inicializar Earth Engine
ee.Initialize(project='light-sunup-288723')

# Definir el área de estudio: Condado de Los Ángeles
la_county = ee.FeatureCollection('TIGER/2018/Counties') \
    .filter(ee.Filter.eq('NAME', 'Los Angeles'))

# Definir el rango de fechas
start_date = ee.Date('2020-01-01')
end_date = ee.Date('2020-12-31')

# Cargar la colección de incendios MODIS Global Burned Area
fires = ee.ImageCollection('MODIS/061/MCD64A1') \
    .filterDate(start_date, end_date) \
    .select('BurnDate') \
    .map(lambda img: img.mask(img)) \
    .map(lambda img: img.reduceToVectors(scale=500, geometryType='centroid', geometry=la_county.geometry(), labelProperty='BurnDate'))

# Convertir la lista de listas de vectores a una sola colección
fires = fires.flatten()

# Obtener las coordenadas de los incendios
def extract_fire_point(feature):
    centroid = feature.geometry().centroid()
    return ee.Feature(centroid, {
        'fecha': '2020-03-01',  # La colección MCD64A1 no tiene 'acq_date', usamos una fecha fija o estimada
        'riesgo': 1
    })

fire_points = fires.map(extract_fire_point)

# Generar puntos aleatorios dentro del área de estudio para áreas sin incendios
non_fire_points = ee.FeatureCollection.randomPoints(**{
    'region': la_county.geometry(),
    'points': 100,
    'seed': 42
})

def random_date_feature(feature):
    rand = ee.Number(feature.id()).multiply(0.12345).sin().abs()
    rand_days = rand.multiply(end_date.difference(start_date, 'day'))
    random_date = start_date.advance(rand_days, 'day')
    return feature.set({
        'fecha': random_date.format('YYYY-MM-dd'),
        'riesgo': 0
    })

non_fire_points = non_fire_points.map(random_date_feature)

# Combinar puntos de incendios y no incendios
sample_points = fire_points.merge(non_fire_points)

# Función para extraer variables en cada punto
def add_variables(feature):
    date = ee.Date(feature.get('fecha'))
    point = feature.geometry()

    is_valid_geom = point.bounds().coordinates().size().gt(0)

    # === NDVI ===
    ndvi_img = ee.ImageCollection('MODIS/061/MOD13Q1') \
        .filterDate(date.advance(-16, 'day'), date) \
        .filterBounds(point) \
        .first()

    ndvi_available = ee.Algorithms.IsEqual(ndvi_img, None).Not()

    ndvi = ee.Algorithms.If(
        is_valid_geom.And(ndvi_available),
        ndvi_img.select('NDVI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=250
        ).get('NDVI'),
        None
    )

    # === LST ===
    lst_img = ee.ImageCollection('MODIS/061/MOD11A1') \
        .filterDate(date.advance(-5, 'day'), date) \
        .filterBounds(point) \
        .first()

    lst_available = ee.Algorithms.IsEqual(lst_img, None).Not()

    lst = ee.Algorithms.If(
        is_valid_geom.And(lst_available),
        lst_img.select('LST_Day_1km').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=1000
        ).get('LST_Day_1km'),
        None
    )

    # === Elevación ===
    elev = ee.Algorithms.If(
        is_valid_geom,
        ee.Image('USGS/SRTMGL1_003').select('elevation') \
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=30
            ).get('elevation'),
        None
    )

    # === Pendiente ===
    slope = ee.Algorithms.If(
        is_valid_geom,
        ee.Terrain.products(ee.Image('USGS/SRTMGL1_003')) \
            .select('slope') \
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=30
            ).get('slope'),
        None
    )

    return feature.set({
        'ndvi': ndvi,
        'temperatura': lst,
        'elevacion': elev,
        'pendiente': slope
    })


# Aplicar la función a todos los puntos
enriched_points = sample_points.map(add_variables)

# Exportar los datos a Google Drive
task = ee.batch.Export.table.toDrive(
    collection=enriched_points,
    description='datos_incendios_LA',
    fileFormat='CSV'
)
task.start()
print("Exportación iniciada. Verifica el estado en la consola de Earth Engine.")
