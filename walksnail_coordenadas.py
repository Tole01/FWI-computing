import cv2

# Global frame variable
current_frame = None

# Define mouse callback function
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: X={x}, Y={y}")
        # Draw a small circle at the clicked point
        cv2.circle(current_frame, (x, y), 5, (0, 255, 0), -1)
        cv2.imshow("Frame", current_frame)

# Open video capture (try 0, or another index if you have multiple cameras)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", click_event)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    current_frame = frame.copy()  # Update global frame
    cv2.imshow("Frame", current_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
