import cv2
import numpy as np

H = np.load("H.npy")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, -30.0)

SIZE = 800
CELL = SIZE // 8

# scale reference logic
DETECT_SIZE = int(CELL * 0.6)
OFFSET = (CELL - DETECT_SIZE) // 2

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break

    warped = cv2.warpPerspective(frame, H, (SIZE, SIZE))

    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

    debug = warped.copy()
    grid = np.zeros((8,8), dtype=int)

    for r in range(8):
        for c in range(8):

            x_start = c * CELL + OFFSET
            y_start = r * CELL + OFFSET

            square = hsv[
                y_start:y_start + DETECT_SIZE,
                x_start:x_start + DETECT_SIZE
            ]

            # GREEN DETECTION (IMPORTANT)
            mask = cv2.inRange(
                square,
                np.array([30,20,20]),
                np.array([95, 255, 255])
            )

            not_green = cv2.bitwise_not(mask)

            piece_pixels = cv2.countNonZero(not_green)

            total_pixels = square.shape[0] * square.shape[1]

            # STRICT THRESHOLD (REFERENCE STYLE)
            if piece_pixels / total_pixels > 0.3:
                grid[r][c] = 1
                color = (0,255,0)
            else:
                grid[r][c] = 0
                color = (0,0,255)

            # 🔥 DRAW SMALL DETECTION BOX (THIS WAS MISSING)
            cv2.rectangle(debug,
                          (x_start, y_start),
                          (x_start + DETECT_SIZE, y_start + DETECT_SIZE),
                          color, 2)

    cv2.imwrite("debug_grid.jpg", debug)

    print(grid)

    break

cap.release()