import cv2
import numpy as np
H = np.load("H.npy")
print(H)
cap = cv2.VideoCapture(0)
print("Current brightness:", cap.get(cv2.CAP_PROP_BRIGHTNESS))
# cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, -50)
# # cap.set(cv2.CAP_PROP_EXPOSURE, -6)
# # cap.set(cv2.CAP_PROP_AUTO_WB, 0)
cap.set(cv2.CAP_PROP_BRIGHTNESS, -30)
print("New brightness:", cap.get(cv2.CAP_PROP_BRIGHTNESS))
SIZE = 800
CELL = SIZE // 8
# scale reference logic
DETECT_SIZE = int(CELL * 0.6)
OFFSET = (CELL - DETECT_SIZE) // 2
def grid_to_fen(grid):
    fen = ""
    for r in range(8):
        empty = 0
        for c in range(8):
            val = grid[r][c]
            if val == 0:
                empty += 1
            else:
                if empty > 0:
                    fen += str(empty)
                    empty = 0
                if val == 1:
                    fen += "P"   # white
                elif val == 2:
                    fen += "p"   # black
        if empty > 0:
            fen += str(empty)
        if r != 7:
            fen += "/"
    return fen
while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera error")
        break
    warped = cv2.warpPerspective(frame, H, (SIZE, SIZE))
    hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)
    value_channel = hsv[:,:,2]   # brightness channel
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
            threshold = piece_pixels / total_pixels
            print(f"Square ({r},{c}) threshold: {threshold:.3f}")
            # STRICT THRESHOLD (REFERENCE STYLE)
            if threshold > 0.3:
                # get brightness values of this square
                value_square = value_channel[
                    y_start:y_start + DETECT_SIZE,
                    x_start:x_start + DETECT_SIZE
                ]
                # only consider piece pixels
                piece_mask = not_green > 0
                if np.any(piece_mask):
                    mean_val = np.mean(value_square[piece_mask])
                    print(mean_val)
                    # 🎯 classify
                    if mean_val > 100:
                        grid[r][c] = 1   # white piece
                        color = (255,255,255)   # white box
                    else:
                        grid[r][c] = 2   # black piece
                        color = (0,255,0)       # green box
                else:
                    grid[r][c] = 0
                    color = (0,0,255)
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
    # 🔥 FEN GENERATION
    fen = grid_to_fen(grid)
    # full FEN (engine format)
    full_fen = fen + " w - - 0 1"
    print("FEN:", full_fen)
    # optional: save last FEN (debug)
    with open("fen.txt", "w") as f:
        f.write(full_fen)        
    break
cap.release()