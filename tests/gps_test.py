from pymavlink import mavutil

# Conexión al puerto UDP
master = mavutil.mavlink_connection('COM14',baud = 115200)

print("Esperando mensajes del dron...")
try:
    while True:
        # Recibir cualquier mensaje
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        if msg:
            # Extraer latitud, longitud y altura
            lat = msg.lat / 1e7        # Convertir de 10^7 grados a grados decimales
            lon = msg.lon / 1e7
            alt = msg.alt / 1000.0     # Convertir de milímetros a metros

            # Imprimir las coordenadas
            print(f"📍 Latitud: {lat:.6f}, Longitud: {lon:.6f}, Altura: {alt:.2f} m")

except KeyboardInterrupt:
    print("Conexión terminada.")