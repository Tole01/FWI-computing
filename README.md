
## Nombre del Proyecto

Fire Detection and Prediction Model
Instituto Tecnológico y de Estudios Superiores de Monterrey, Campus Monterrey
MR3002B.501: Diseño e implementación de Sistemas Mecatrónicos
Socio Formador: Green Tech Innovation (GTI)

## Tabla de Contenidos

- [Instalación](#instalación)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Configuración del Sistena](#configuración-del-sistema)
- [Funcionamiento](#funcionamiento)
- [Licencias](#licencias)
- [Autor](#autor)

## Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/Tole01/FWI-computing.git
   cd tu_proyecto
   ```

2. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv env
   source env/bin/activate   # En Windows: env\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Instala las librerías necesarias en `requirements.txt`.
2. Ejecuta el archivo `main.py`.
3. Espera unos minutos a que se detecte el fuego por medio de las cámaras y realice la subsecuente predicción.
4. Cuando la aplicación se despliegue, abre tu navegador en `http://localhost:5000`.

## Estructura del Proyecto

```
FWI-COMPUTING/
├── tests/                 # Tests
├── templates/
│   └── leaflet.html       # Mapa en 2D
│   └── mapbox3d.html      # Mapa en 3D
├── README.md              # READ.ME
├── requirements.txt       # Lista de dependencias
├── riesgo.geojson         # Archivo generado con los datos de riesgo
├── fire_s.pt              # Modelo YOLOv8 entrenado
├── firetest11.jpg         # Imagen utilizada en tests
├── main.py                # Archivo de donde se llaman todas las funciones; servidor Flask
├── classes.py             # xx
├── coordinates.py         # xx
├── display.py             # xx
├── fire_detection.py      # xx
├── geojson_gen.py         # xx
├── mesh.py                # xx
├── temperature.py         # xx
└── utils.py               # xx
```

## Requisitos

Este proyecto usa las siguientes librerías:

```txt
aenum==3.1.16
blinker==1.9.0
certifi==2025.4.26
charset-normalizer==3.4.2
click==8.2.0
contourpy==1.3.2
cycler==0.12.1
dataclasses-json==0.6.7
filelock==3.18.0
Flask==3.1.1
fonttools==4.58.0
fsspec==2025.3.2
future==1.0.0
geojson==2.5.0
idna==3.10
iso8601==2.1.0
itsdangerous==2.2.0
Jinja2==3.1.6
kiwisolver==1.4.8
lxml==5.4.0
MarkupSafe==3.0.2
marshmallow==3.26.1
matplotlib==3.10.3
mpmath==1.3.0
mypy_extensions==1.1.0
networkx==3.4.2
numpy==2.2.5
oauthlib==3.2.2
opencv-python==4.11.0.86
opencv-python-headless==4.11.0.86
packaging==25.0
pandas==2.2.3
pillow==11.2.1
psutil==7.0.0
py-cpuinfo==9.0.0
pymavlink==2.4.43
pyparsing==3.2.3
pyproj==3.7.1
python-dateutil==2.9.0.post0
pytz==2025.2
PyYAML==6.0.2
requests==2.32.3
requests-oauthlib==2.0.0
scipy==1.15.3
seaborn==0.13.2
sentinelhub==3.11.1
serial==0.0.97
setuptools==80.4.0
shapely==2.1.0
six==1.17.0
sympy==1.14.0
tifffile==2025.5.10
tomli==2.2.1
tomli_w==1.2.0
torch==2.7.0
torchvision==0.22.0
tqdm==4.67.1
typing-inspect==0.9.0
typing_extensions==4.13.2
tzdata==2025.2
ultralytics==8.3.133
ultralytics-thop==2.0.14
urllib3==2.4.0
utm==0.8.1
Werkzeug==3.1.3
wheel==0.45.1
```

Instálalas con:

```bash
pip install -r requirements.txt
```

## Configuración del Sistema

Antes de ejecutar el sistema, asegúrate de configurar los siguientes parámetros según las características de tu dron y cámara:

- FOV_optica_horizontal –> Campo de visión horizontal de la cámara óptica (en grados)
- FOV_optica_vertical -> Campo de visión vertical de la cámara óptica (en grados)
- FOV_termica_horizontal -> Campo de visión horizontal de la cámara térmica (en grados)
- FOV_termica_vertical -> Campo de visión vertical de la cámara térmica (en grados)
- thermal_width – Resolución horizontal de la matriz térmica (en pixeles)
- thermal_height – Resolución vertical de la matriz térmica (en pixeles)
- COM_antena - puerto donde se conecta la antena del dron
- COM_esp - puerto donde se conecta el ESP32

Estos parámetros se deben definir en el archivo `config.py`.

## Funcionamiento

Este proyecto realiza la detección de incendios y la generación automática de un mapa de riesgo geoespacial a partir de imágenes ópticas y térmicas capturadas por un dron. A continuación se describen los pasos clave del proceso:

1. Detección de Incendios (Visión por Computadora)
Se utiliza un modelo YOLOv8 entrenado (fire_s.pt) para detectar incendios en imágenes capturadas por la cámara óptica del dron.

Se identifican las coordenadas en píxeles del centro del incendio.

2. Matriz de Temperatura (Sensor Térmico)
Se obtiene una matriz térmica simulada o real representando la temperatura en cada celda de la imagen.

La matriz es normalizada para escalar sus valores y facilitar el análisis posterior.

3. Georreferenciación
Se recuperan las coordenadas GPS y altura del dron (por ejemplo, desde ArduPilot).

Se convierte la posición del incendio (en píxeles) a coordenadas geográficas (lat/lon) utilizando parámetros de la cámara (campo de visión, dimensiones, etc.).

4. Análisis de Riesgo (Mallado e Interpolación)
Se realiza una segmentación por malla sobre la imagen para asociar regiones a riesgos térmicos.

Se aplica interpolación por vecinos más cercanos (Nearest Neighbor Interpolation) para suavizar el análisis espacial del riesgo.

Se generan visualizaciones de calor y riesgo en formato imagen.

5. Generación de GeoJSON
A partir del análisis de riesgo y las coordenadas geográficas, se genera un archivo riesgo.geojson que representa el mapa de riesgo en formato compatible con aplicaciones web y GIS.

6. Visualización Web (2D y 3D)
Se levanta una aplicación con Flask que permite visualizar:
- Un mapa 2D interactivo con Leaflet.js.
- Una vista 3D del riesgo usando Mapbox.
- El archivo riesgo.geojson es servido como recurso para ambas vistas.

## Licencias

[Mapbox](token)            -->      Es necesario crear una cuenta y utilizar el token generado en `mapbox3d.html` y `utils.py`.
[OpenWeather](key)         -->      xx
[SentinelHub](user...)     -->      xx
[etc]...

## Autor

Equipo 2 (Integrantes):

Nombre                              Correo               Github
Christopher Santiago Ducey          a01174113@tec.mx     @csantiducey
Joel Adrián Elizondo González       a01721040@tec.mx     @jaeger26
Jacobo Torres Cepeda                a00832642@tec.mx     @jacobot27
Hector Andrés González González     a01284602@tec.mx     @handrescg