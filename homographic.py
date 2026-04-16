import cv2
import numpy as np

points = []

img = cv2.imread("capture.jpg")

if img is None:
    print("❌ Image not found")
    exit()

clone = img.copy()

SIZE = 800

# 🔥 resize for display
DISPLAY_WIDTH = 800
h, w = img.shape[:2]
scale = DISPLAY_WIDTH / w
display_img = cv2.resize(img, (int(w * scale), int(h * scale)))

def compute_homography():
    src = np.array(points, dtype=np.float32)

    dst = np.array([
        [0, 0],
        [SIZE-1, 0],
        [0, SIZE-1],
        [SIZE-1, SIZE-1]
    ], dtype=np.float32)

    H = cv2.getPerspectiveTransform(src, dst)

    print("\n✅ Homography Matrix:\n", H)

    np.save("H.npy", H)
    print("Saved H.npy")

    warped = cv2.warpPerspective(clone, H, (SIZE, SIZE))
    cv2.imwrite("warped.jpg", warped)
    print("Saved warped.jpg (VERIFY THIS!)")

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) >= 4:
            print("Already selected 4 points")
            return

        # 🔥 convert back to original scale
        orig_x = int(x / scale)
        orig_y = int(y / scale)

        points.append((orig_x, orig_y))

        # draw on display image
        cv2.circle(display_img, (x, y), 6, (0, 0, 255), -1)

        cv2.putText(display_img, f"{len(points)}", (x+10, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        print(f"Point {len(points)}: {orig_x}, {orig_y}")

        cv2.imwrite("clicked.jpg", display_img)

        if len(points) == 4:
            print("\nSelected points:", points)
            compute_homography()
            print("\nPress 'q' to exit...")

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_event)

while True:
    cv2.imshow("image", display_img)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()