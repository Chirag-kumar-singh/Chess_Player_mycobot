import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera not detected")
    exit()

print("Capturing image...")

ret, frame = cap.read()

if ret:
    cv2.imwrite("capture.jpg", frame)
    print("Image saved as capture.jpg")
else:
    print("Failed to capture")

cap.release()
