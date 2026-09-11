import cv2

# Open your webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to access camera")
        break

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect edges
    edges = cv2.Canny(gray, 100, 200)

    # Show original + edges
    cv2.imshow("Camera", frame)
    cv2.imshow("Edges", edges)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()