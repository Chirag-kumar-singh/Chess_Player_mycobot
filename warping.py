import cv2

points = []

img = cv2.imread("capture.jpg")

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))

        # Draw circle
        cv2.circle(img, (x, y), 8, (0, 0, 255), -1)

        # Label point
        cv2.putText(img, f"{len(points)}", (x+10, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

        print(f"Point {len(points)}: {x}, {y}")

        # Save updated image
        cv2.imwrite("clicked.jpg", img)

        # Auto exit after 4 points
        if len(points) == 4:
            print("Selected points:", points)
            exit()

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_event)

while True:
    cv2.imshow("image", img)

    # press 'q' to exit manually
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
