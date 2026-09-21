import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. Convert to Grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. Invert brightness so dark features (hair, eyes) get the high/red end of the spectrum
    inverted_gray = cv2.bitwise_not(gray)

    # 3. Apply false color map (JET, RAINBOW, or TURBO)
    thermal_effect = cv2.applyColorMap(inverted_gray, cv2.COLORMAP_JET)

    cv2.imshow("Thermal / Pop Art Effect", thermal_effect)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()