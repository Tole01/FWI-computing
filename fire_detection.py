import cv2
from ultralytics import YOLO
from temperature import get_temp_matrix, detectar_hotspots

def detect_fire(model, fire = 0):
    """
    Loop que abre la cámara óptica y busca incendios.
    Si detecta fuego, regresa fire = 1 y la imagen óptica capturada.
    
    Args:
        model: YOLOv8 modelo utilizado para la inferencia
        fire (int): 1 si ya había fuego, 0 si se está buscando.
    
    Returns:
        cx (int) Coordenada x del centroide del fuego.
        cy (int) Coordenada y del centroide del fuego.
        img_optica (numpy array) Imagen de la cámara en el momento de detección.
        fire_coordinates: Lista de tuplas que contienen la coordenada (cx, cy) del centro del fuego
    """
    model = YOLO(r"fire_s.pt") #Modelo de deteccion entrenado
    cap = cv2.VideoCapture(0)  # Ajustar a cámara correspondiente
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        exit()

    img_optica = None  # Inicializamos variable
    frame_count = 0 

    while not fire:
        ret, frame = cap.read()
        if not ret:
            print("No se pudo leer el frame de la cámara.")
            break
        
        thermal_matrix = get_temp_matrix() # Obtener temperatura 120X160
        hotspots, t_amb = detectar_hotspots(thermal_matrix)

        # Ejecutar inferencia cada 3 frames
        if frame_count % 3 == 0:
            frame = cv2.imread(r'firetest11.jpg') #ejemplo se borra
            resized_frame = cv2.resize(frame, (640, 360))
            results = model(resized_frame, conf=0.3)[0] #resultados de YOLO en el frame
            #results = model.predict(source=r"firetest11.jpg", conf=0.4)[0] #ejemplo se borra
            annotated_frame = results.plot()
            fire_coordinates = []  # Lista para almacenar los pares (cx, cy)
            for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                x1, y1, x2, y2 = box
                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)
                fire_coordinates.append((cx, cy))  # Agregar el par (cx, cy) a la lista

                class_name = results.names[int(cls)]

                if class_name == 'fire' and hotspots: # Si se detecta fuego y hay hotspots
                    fire = 1
                    img_optica = frame.copy()  # Guardamos la imagen original en el momento de detección
                    print(f"🔥 Incendio detectado - Centroide: ({cx}, {cy}) - Confianza: {conf:.2f}")

                    cv2.circle(annotated_frame, (cx, cy), 5, (0, 0, 255), -1)
                    label = f"{class_name} ({conf:.2f})"
                    cv2.putText(annotated_frame, label, (cx + 10, cy),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    
         
            cv2.imshow("Detección de Incendio - Webcam", annotated_frame)

            # Permitir salir manualmente presionando 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Saliendo manualmente...")
                break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    return img_optica,cx,cy,fire_coordinates, hotspots, t_amb, thermal_matrix
 