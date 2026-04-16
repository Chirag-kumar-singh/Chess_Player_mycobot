import cv2

cap = cv2.VideoCapture(0)
print("Current brightness:", cap.get(cv2.CAP_PROP_BRIGHTNESS))

# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, -50)
# # cap.set(cv2.CAP_PROP_EXPOSURE, -6)

# # cap.set(cv2.CAP_PROP_AUTO_WB, 0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, -30)
print("New brightness:", cap.get(cv2.CAP_PROP_BRIGHTNESS))

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
