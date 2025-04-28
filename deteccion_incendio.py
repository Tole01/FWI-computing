import cv2
from ultralytics import YOLO

def detect_fire(fire):
    """
    Loop que abre la cámara óptica y busca incendios.
    Si no hay fuego, se queda en un loop infinito escaneando.
    
    Args:
        fire (int): Variable que indica si hay fuego o no. 1 si hay fuego, 0 si no hay fuego.
    
    Returns:
        fire (int): Devuelve 1 si se detecta fuego, 0 si no.
    """
    # Cargar el modelo
    model = YOLO(r"fire_s.pt")
    
    # Conectar a la cámara óptica
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        exit()

    while fire == 0:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame de la cámara.")
            break

        # Ejecutar inferencia con umbral
        results = model(frame, conf=0.5)[0]

        # Dibujar cajas en el frame
        annotated_frame = results.plot()

        # Buscar incendios
        for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
            x1, y1, x2, y2 = box
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            class_name = results.names[int(cls)]

            if class_name == 'fire':
                fire = 1
                print(f"🔥 Incendio detectado - Centroide: ({cx}, {cy}) - Confianza: {conf:.2f}")

                # Dibujar círculo rojo en el centroide
                cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)
                label = f"{class_name} ({conf:.2f})"
                cv2.putText(annotated_frame, label, (cx + 10, cy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Mostrar la imagen
        cv2.imshow("🔥 Detección de Incendio - Webcam", annotated_frame)

        # Permitir salir manualmente presionando 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Saliendo manualmente...")
            break

    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()

    return fire