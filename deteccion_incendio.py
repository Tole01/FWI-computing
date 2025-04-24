from ultralytics import YOLO
import cv2

# Cargar modelo entrenado
model = YOLO(r"C:\Users\jacob\Documents\itesm\8vo semestre\Bloque\Codigo\gti-cv-app\Models\fire_s.pt")

# Conectar a la cámara
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("No se pudo abrir la cámara.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Ejecutar inferencia con umbral
    results = model(frame, conf=0.5)[0]

    # Dibujar cajas en el frame
    annotated_frame = results.plot()

    # Obtener los centroides de los incendios
    for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
        x1, y1, x2, y2 = box
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        class_name = results.names[int(cls)]

        if class_name == 'fire':
            print(f"🔥 Incendio detectado - Centroide: ({cx}, {cy}) - Confianza: {conf:.2f}")

            # Dibujar círculo rojo en el centroide
            cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)
            # Etiqueta opcional
            label = f"{class_name} ({conf:.2f})"
            cv2.putText(annotated_frame, label, (cx + 10, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Mostrar la imagen
    cv2.imshow("🔥 Detección de Incendio - Webcam", annotated_frame)

    # Salir con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
