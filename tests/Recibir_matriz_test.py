import serial

def recibir_matriz(ser):
    matriz = []
    leyendo = False
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line == "<START>":
            leyendo = True
            matriz = []
            continue
        elif line == "<END>":
            break
        elif leyendo:
            try:
                fila = [int(x) for x in line.split(",")]
                if len(fila) == 9:
                    matriz.append(fila)
            except ValueError:
                continue  # Ignora líneas corruptas
    return matriz

# Ajusta el puerto
ser = serial.Serial('COM7', 115200, timeout=1)

while True:
    matriz = recibir_matriz(ser)
    print("Matriz recibida:")
    for fila in matriz:
        print(fila)
