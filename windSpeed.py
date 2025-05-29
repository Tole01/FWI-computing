import leafmap
import geemap
import ee
import webbrowser
ee.Authenticate()
ee.Initialize(project='light-sunup-288723')

url = "https://github.com/opengeos/datasets/releases/download/raster/wind_global.nc"
filename = "wind_global.nc"
leafmap.download_file(url, output=filename, overwrite=True)
data = leafmap.read_netcdf(filename)
print(data)

tif = "wind_global.tif"
leafmap.netcdf_to_tif(filename, tif, variables=["u_wind", "v_wind"], shift_lon=True)
geojson = ("https://github.com/opengeos/leafmap/raw/master/examples/data/countries.geojson")

m = leafmap.Map(center=[34.21113114902449,-118.1138591514406],layers_control=True,zoom=7)
m.add_basemap("CartoDB.DarkMatter")
m.add_velocity(
    filename,
    zonal_speed="u_wind",
    meridional_speed="v_wind",
    color_scale=[
        "rgb(0,0,150)",
        "rgb(0,150,0)",
        "rgb(255,255,0)",
        "rgb(255,165,0)",
        "rgb(150,0,0)",
    ],
)
m.to_html("windMap.html")
webbrowser.open("windMap.html")