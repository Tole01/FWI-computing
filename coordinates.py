from pymavlink import mavutil

def get_coordinates():
    """
    Se conecta al dron vía MAVLink y retorna la latitud y longitud actuales.
    Retorna:
        (lat, lon): Tuple[float, float] con coordenadas GPS en grados decimales
    """
    try:
        # Conexión al puerto UDP donde MAVProxy reenvía los datos
        master = mavutil.mavlink_connection('udp:127.0.0.1:14550')
        master.wait_heartbeat(timeout=10)
        print("✅ Conectado al dron. Esperando datos GPS...")

        # Espera a recibir datos GPS válidos
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=10)
        if msg:
            lat = msg.lat / 1e7
            lon = msg.lon / 1e7
            return lat, lon
        else:
            print("❌ No se recibió mensaje GPS a tiempo.")
            return None
    except Exception as e:
        print(f"❌ Error al obtener coordenadas: {e}")
        return None
