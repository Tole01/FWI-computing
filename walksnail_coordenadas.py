import cv2

# Define a mouse callback function
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: X={x}, Y={y}")
        # Optionally draw a circle where clicked
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Frame", param)

# Open video capture (adjust the index if needed, or use video file path)
cap = cv2.VideoCapture(0)  # 0 usually means first connected camera device

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    cv2.imshow("Frame", frame)

    # Set mouse callback on the frame window
    cv2.setMouseCallback("Frame", click_event, frame.copy())

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
