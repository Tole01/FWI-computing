import serial
import time
import numpy as np
import matplotlib.pyplot as plt


def get_temp_matrix(puerto, baudios=115200, timeout=20):
    try:
        ser = serial.Serial(puerto, baudios, timeout=1)
    except serial.SerialException as e:
        print(f"Error al abrir el puerto serial: {e}")
        return None

    print("Esperando <START>...")
    start_time = time.time()
    buffer = ""

    # Esperar hasta encontrar <START>
    while True:
        if time.time() - start_time > timeout:
            print("Tiempo máximo de espera alcanzado.")
            ser.close()
            return None

        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += chunk
            if "<START>" in buffer:
                buffer = buffer.split("<START>")[1]
                break

    print("<START> detectado. Leyendo datos hasta <END>...")

    # Leer hasta <END>
    while "<END>" not in buffer:
        if ser.in_waiting:
            chunk = ser.read(ser.in_waiting).decode(errors='ignore')
            buffer += chunk
        else:
            time.sleep(0.01)

    ser.close()
    datos_brutos = buffer.split("<END>")[0].strip()
    filas = datos_brutos.strip().splitlines()

    try:
        matriz = [list(map(float, fila.strip().split(','))) for fila in filas]
        return np.array(matriz, dtype=np.float32)
    except Exception as e:
        print(f"Error al convertir a matriz: {e}")
        return None
    
if __name__ == "__main__":
    matriz_temp = get_temp_matrix('COM3')
    
    # Mostrar heatmap
    plt.figure(figsize=(10, 6))
    plt.imshow(matriz_temp, cmap='inferno')
    plt.colorbar(label="Temperatura (°C)")
    plt.title("Mapa de calor con hotspots")
    plt.tight_layout()
    plt.show()