# import xarray as xr
# ds = xr.open_dataset('wind_global.nc')
# print(ds)

import os
import folium
import rasterio

tif = os.path.abspath("wind_global.tif")
print(tif)

# Abrir el raster para obtener los límites
with rasterio.open(tif) as src:
    bounds = src.bounds
    img = src.read(1)

# Calcular los límites en lat/lon
image_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

m = folium.Map(location=[(bounds.top + bounds.bottom)/2, (bounds.left + bounds.right)/2], zoom_start=2)

folium.raster_layers.ImageOverlay(
    image=img,
    bounds=image_bounds,
    opacity=0.6,
    name="u_wind"
).add_to(m)

folium.LayerControl().add_to(m)
m.save("wind_speed.html")
print("Mapa guardado como wind_speed.html")