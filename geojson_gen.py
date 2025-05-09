import geojson

def generar_geojson():
    
    # Matriz ejemplo (latitud, longitud, nivel de riesgo [0–1])
    matriz = [
        (34.05, -118.25, 0.2),
        (34.06, -118.25, 0.6),
        (34.07, -118.25, 0.9)
    ]

    step = 0.01  # tamaño del cuadrado en grados/coordenadas geográficas (1 grado = 111 km aprox)

    
    features = []

    for lat, lon, riesgo in matriz:
        coords = [[
            [lon, lat],
            [lon + step, lat],
            [lon + step, lat + step],
            [lon, lat + step],
            [lon, lat]
        ]]
        feature = geojson.Feature(
            geometry=geojson.Polygon(coords),
            properties={"riesgo": riesgo}
        )
        features.append(feature)

    geojson_obj = geojson.FeatureCollection(features)

    with open("riesgo.geojson", "w") as f:
        geojson.dump(geojson_obj, f)