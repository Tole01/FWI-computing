import cv2
from ultralytics import YOLO
import math

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

        # Ejecutar inferencia cada 3 frames
        if frame_count % 3 == 0:
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

                if class_name == 'fire':
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

    return img_optica,cx,cy,fire_coordinates


def map_optical_pixel_to_thermal(cx,cy,height,res_x_opt, res_y_opt,baseline =0.05):
    """
    Mapea las coordenadas ópticas (cx, cy) a las coordenadas térmicas (x, y).
    Args:
        cx (int): Coordenada x de interes en la imagen óptica.
        cy (int): Coordenada y de interes en la imagen óptica.
        height (float): Altura del dron.
        res_x_opt (float): Resolución en x de la cámara óptica.
        res_y_opt (float): Resolución en y de la cámara óptica.
        baseline (float): Distancia entre las cámaras óptica y térmica en metros
    Returns:
        x (int): Coordenada x correspondiente en la imagen térmica.
        y (int): Coordenada y correspondiente en la imagen térmica.
    """
    res_x_therm = 80 #pixeles de ancho de la imagen termica
    res_y_therm = 60 #pixeles de alto de la imagen termica
    fov_x_opt = 157.1 #Campo de visión en x de la cámara óptica
    fov_y_opt = 140.4 #Campo de visión en y de la cámara óptica
    fov_x_therm = 95 #Campo de visión en x de la cámara térmica
    fov_y_therm = 71.25 #Campo de visión en y de la cámara térmica

    # FOV a radianes
    fx_opt = math.radians(fov_x_opt)
    fy_opt = math.radians(fov_y_opt)
    fx_therm = math.radians(fov_x_therm)
    fy_therm = math.radians(fov_y_therm)

    # Tamaño físico en el suelo (óptica)
    width_opt = 2 * height * math.tan(fx_opt / 2)
    height_opt = 2 * height * math.tan(fy_opt / 2)

    # Tamaño físico en el suelo (térmica)
    width_therm = 2 * height * math.tan(fx_therm / 2)
    height_therm = 2 * height * math.tan(fy_therm / 2)

    # Tamaño de píxel en el suelo
    dx_opt = width_opt / res_x_opt
    dy_opt = height_opt / res_y_opt
    dx_therm = width_therm / res_x_therm
    dy_therm = height_therm / res_y_therm

    # Coordenadas físicas desde el centro óptico
    X = (cx - res_x_opt / 2) * dx_opt
    Y = (cy - res_y_opt / 2) * dy_opt

    # Ajuste por desplazamiento entre cámaras (térmica a la izquierda en -X)
    X_therm = X + baseline
    Y_therm = Y

    # Convertir coordenadas físicas a píxeles térmicos
    dx = (X_therm / dx_therm) + res_x_therm / 2
    dy = (Y_therm / dy_therm) + res_y_therm / 2

    return dx, dy
