import cv2
import numpy as np
import os

def empty_callback(x):
    pass

cv2.namedWindow("Trackbars")
cv2.resizeWindow("Trackbars", 400, 350)
cv2.createTrackbar("Blue", "Trackbars", 100, 200, empty_callback)
cv2.createTrackbar("Green", "Trackbars", 100, 200, empty_callback)
cv2.createTrackbar("Red", "Trackbars", 100, 200, empty_callback)
cv2.createTrackbar("Brightness", "Trackbars", 50, 100, empty_callback)

script_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(script_dir, "gambar.png")

img = cv2.imread(image_path)

if img is None:
    print(f"Path yang dicari Python: {image_path}")
    raise FileNotFoundError("File gambar.png tetap tidak terbaca!")

cap = cv2.VideoCapture(0)
mode = 'image'

while True:
    b_scale = cv2.getTrackbarPos("Blue", "Trackbars") / 100.0
    g_scale = cv2.getTrackbarPos("Green", "Trackbars") / 100.0
    r_scale = cv2.getTrackbarPos("Red", "Trackbars") / 100.0
    brightness = cv2.getTrackbarPos("Brightness", "Trackbars") - 50

    if mode == 'image':
        frame = img.copy()
    else:
        ret, frame = cap.read()
        if not ret:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

    b, g, r = cv2.split(frame.astype(np.float32))

    b = np.clip(b * b_scale + brightness, 0, 255)
    g = np.clip(g * g_scale + brightness, 0, 255)
    r = np.clip(r * r_scale + brightness, 0, 255)

    filtered = cv2.merge([b, g, r]).astype(np.uint8)

    cv2.putText(frame, f"Original | Mode: {mode.upper()} (1: Img, 2: Cam)", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(filtered, "Color Adjusted", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    combined = np.hstack((frame, filtered))

    cv2.imshow("Preview", combined)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        mode = 'image'
    elif key == ord('2'):
        mode = 'camera'

cap.release()
cv2.destroyAllWindows()