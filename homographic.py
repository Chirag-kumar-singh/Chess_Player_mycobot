import cv2
import numpy as np

points = []

img = cv2.imread("capture.jpg")
clone = img.copy()   # keep original safe

SIZE = 800  # output warped size

def compute_homography():
    src = np.array(points, dtype=np.float32)

    # IMPORTANT ORDER: TL, TR, BL, BR
    dst = np.array([
        [0, 0],
        [SIZE-1, 0],
        [0, SIZE-1],
        [SIZE-1, SIZE-1]
    ], dtype=np.float32)

    H = cv2.getPerspectiveTransform(src, dst)

    print("\n✅ Homography Matrix:\n", H)

    # Save matrix
    np.save("H.npy", H)
    print("Saved H.npy")

    # Warp image for verification
    warped = cv2.warpPerspective(clone, H, (SIZE, SIZE))
    cv2.imwrite("warped.jpg", warped)
    print("Saved warped.jpg (VERIFY THIS!)")

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:

        if len(points) >= 4:
            print("Already selected 4 points")
            return

        points.append((x, y))

        # Draw point
        cv2.circle(img, (x, y), 8, (0, 0, 255), -1)

        # Label
        cv2.putText(img, f"{len(points)}", (x+10, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        print(f"Point {len(points)}: {x}, {y}")

        cv2.imwrite("clicked.jpg", img)

        # When 4 points selected
        if len(points) == 4:
            print("\nSelected points:", points)

            compute_homography()

            print("\nPress 'q' to exit...")

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_event)

while True:
    cv2.imshow("image", img)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break

cv2.destroyAllWindows()
