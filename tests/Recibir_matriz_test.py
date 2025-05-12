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
                if len(fila) == 16:
                    matriz.append(fila)
            except ValueError:
                continue  # Ignora líneas corruptas
    return matriz

# Ajusta el puerto según tu sistema
ser = serial.Serial('COM7', 115200, timeout=1)

while True:
    matriz = recibir_matriz(ser)
    if len(matriz) == 9:
        print("✅ Matriz recibida (9x16):")
        for fila in matriz:
            print(fila)
    else:
        print("❌ Matriz incompleta o malformada.")
