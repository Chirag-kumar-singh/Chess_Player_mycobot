from pymycobot.mycobot import MyCobot
import time
import sys
import tty
import termios

# ---------------- CONFIG ----------------
PORT = "/dev/ttyTHS1"
BAUD = 1000000
SPEED = 10
STEP = 1


GRIP_OPEN = 30
GRIP_OPEN_ZERO = 40
GRIP_CLOSE = 0
GRIP_SPEED = 50
# ----------------------------------------

LIMITS = [
    (-168,168),
    (-140,140),
    (-150,150),
    (-150,150),
    (-155,160),
    (-180,180)
]

def clamp(angles):
    return [max(min(a, mx), mn) for a, (mn, mx) in zip(angles, LIMITS)]

def get_key():
    """Capture single key press (no Enter needed)"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

print("Connecting to myCobot...")
mc = MyCobot(PORT, BAUD)
time.sleep(2)

mc.power_on()
time.sleep(1)

current_angles = mc.get_angles()
if not current_angles:
    current_angles = [0,0,0,0,0,0]

print("\n🎮 Control Started!")
print("""
Controls:
q/a → J1 +/-
w/s → J2 +/-
e/d → J3 +/-
r/f → J4 +/-
t/g → J5 +/-
y/h → J6 +/-

o → open gripper
c → close gripper

i - initial position
b - back position
z → zero position
x → exit
""")

key_map = {
    'q': (0, +STEP), 'a': (0, -STEP),
    'w': (1, +STEP), 's': (1, -STEP),
    'e': (2, +STEP), 'd': (2, -STEP),
    'r': (3, +STEP), 'f': (3, -STEP),
    't': (4, +STEP), 'g': (4, -STEP),
    'y': (5, +STEP), 'h': (5, -STEP),
}

position_map = {
    "11": [-4, -71, -8, -1, -1, 40],
    "21": [3, -67, -14, -2, -1, 49],
    "31": [6.279999999999999, -66.59, -11.82, -3.0, 1.7000000000000002, 48.92],
    "41": [4.279999999999999, -69.59, -12.82, 1.0, 7.699999999999999, 53.92],
    "51": [9.28, -65.59, -20.82, 5.0, 7.699999999999999, 47.92],
    "61": [19.28, -64.59, -21.82, 5.0, 3.6999999999999993, 60.92],
    "71": [31.28, -47.54, -64.06, 35.85, -8.43, 39.959999999999994],
    "81": [30.91, -55.17, -53.65, 33.92, 1.3900000000000001, 35.57],
    "12": [-7.129999999999999, -64.46000000000001, -20.560000000000002, 0.16000000000000014, -0.16999999999999993, 37.7],
    "22": [-0.129999999999999, -61.46000000000001, -25.560000000000002, 1.1600000000000001, -0.16999999999999993, 37.7],
    "32": [5.870000000000001, -61.46000000000001, -26.560000000000002, -1.8399999999999999, -0.16999999999999993, 49.7],
    "42": [12.870000000000001, -61.46000000000001, -23.560000000000002, -4.84, -1.17, 58.7],        #falling
    "52": [20.87, -52.46000000000001, -41.56, 6.16, -3.17, 65.7],
    "62": [21.28, -56.59, -36.82, 7.0, 3.6999999999999993, 64.92],
    "72": [28.28, -55.59, -36.82, 7.0, 0.6999999999999993, 73.92],
    "82": [30.49, -75.33, 2.6000000000000014, -16.010000000000005, 4.7, 71.03],
    "13": [-9.129999999999999, -42.46000000000001, -67.56, 28.16, 0.8300000000000001, 37.7],
    "23": [-1.129999999999999, -30.460000000000008, -90, 43.16, -1.17, 41.7],
    "33": [5.870000000000001, -30.460000000000008, -90, 40.16, -1.17, 48.7],
    "43": [13.870000000000001, -30.460000000000008, -90, 38.16, -2.17, 55.7],
    "53": [19.87, -28.460000000000008, -90, 37.16, -2.17, 64.7],                                    #stucking
    "63": [27.98, -29.35, -90, 37.89, -3.81, 72.07],                                                 #stucking
    "73": [28.28, -49.59, -46.82, 7.0, 3.6999999999999993, 73.92],
    "83": [35.28, -52.59, -41.82, 6.0, 2.6999999999999993, 79.92],
    "14": [-9.129999999999999, -34.46000000000001, -79.56, 28.16, 0.8300000000000001, 37.7],
    "24": [-1.129999999999999, -29.460000000000008, -89.56, 33.16, -0.16999999999999993, 43.7],
    "34": [6.870000000000001, -29.460000000000008, -90, 32.159999999999997, -1.17, 49.7],
    "44": [12.870000000000001, -29.460000000000008, -88, 30.159999999999997, -1.17, 59.7],            #stucking
    "54": [19.87, -25.460000000000008, -95, 34.16, 1.83, 65.7],                                       #stucking
    "64": [27.98, -24.35, -97, 37.89, 0.1899999999999995, 72.07],                                     #stucking
    "74": [28.28, -47.59, -52.82, 4.0, 7.699999999999999, 73.92],                                     #stucking
    "84": [34.28, -37.59, -70.82, 19.0, 6.699999999999999, 79.92],
    "15": [-10.129999999999999, -30.460000000000008, -83.56, 25.159999999999997, -0.16999999999999993, 35.7],
    "25": [0.870000000000001, -29.460000000000008, -88, 25.159999999999997, -2.17, 46.7],
    "35": [9.870000000000001, -29.460000000000008, -87, 22.159999999999997, -3.17, 53.7],
    "45": [15.870000000000001, -29.460000000000008, -88, 22.159999999999997, -1.17, 59.7],
    "55": [22.87, -29.460000000000008, -89, 20.159999999999997, -0.16999999999999993, 86.7],             #stucking
    "65": [29.98, -16.35, -110, 39.89, 1.1899999999999995, 75.07],                                       #stucking
    "75": [37.980000000000004, -17.35, -106, 37.89, 0.1899999999999995, 84.07],                          #stucking
    "85": [37.28, -29.590000000000003, -87.82, 26.0, 6.699999999999999, 81.92],                          #stucking
    "16": [-10.129999999999999, -32.46000000000001, -83, 19.159999999999997, -2.17, 35.7],
    "26": [0.87, -27.46, -88.5, 17.16, -2.17, 46.7],
    "36": [6.869999999999999, -31.46, -86.5, 16.16, -0.16999999999999993, 53.7],
    "46": [13.87, -28.46, -88, 15.16, 1.83, 61.7],
    "56": [28.87, -25.460000000000008, -90, 14.159999999999997, -0.16999999999999993, 68.7],
    "66": [26.870000000000005, -29.460000000000008, -90, 19.159999999999997, 6.83, 70.7],                   #falling
    "76": [44.980000000000004, -12.350000000000001, -115, 38.89, 1.1899999999999995, 88.07],                #stucking
    "86": [40.28, -21.590000000000003, -100.82, 32.0, 8.7, 88.92],
    "17": [-10.13, -33.46, -82.44, 12.16, -4.17, 35.7],                                                     #distorting
    "27": [0.0, -0.3500000000000014, -130, 43.45, -2.8599999999999994, 45.35],
    "37": [13.0, 3.6499999999999986, -134, 40.45, -2.8599999999999994, 57.35],                              #stucking
    "47": [23.0, 5.649999999999999, -136, 41.45, -1.8599999999999994, 67.35],                               #stucking
    "57": [31.0, 5.649999999999999, -136, 41.45, 0.14000000000000057, 74.35],                               #stucking
    "67": [42.0, 5.649999999999999, -136, 41.45, -0.8599999999999994, 85.35],                                #stucking
    "77": [52.0, 4.649999999999999, -136, 44.45, -2.8599999999999994, 98.35],                                 #falling
    "87": [60.0, 4.649999999999999, -139, 51.45, -2.8599999999999994, 103.35],                                #fallingr(77)
    "18": [-10.0, 8.649999999999999, -140, 44.45, -2.8599999999999994, 34.35],
    "28": [0.0, 5.649999999999999, -142, 46.45, -2.8599999999999994, 45.35],
    "38": [15.0, 13.649999999999999, -140, 33.45, -2.8599999999999994, 59.35],
    "48": [32.0, 14.649999999999999, -143, 33.45, -1.8599999999999994, 78.35],
    "58": [40.0, 14.649999999999999, -141, 32.45, -0.8599999999999994, 85.35],                               #stucking
    "68": [65.0, 24.65, -145, 25.450000000000003, -4.859999999999999, 111.35],                               #falling(78)
    "78": [69.0, 35.65, -150, 25.450000000000003, -1.8599999999999994, 114.35],                              #stucking(88)
    "88": [69.0, 10.649999999999999, -137, 37.45, -0.8599999999999994, 113.35],
    "camera": [32.120000000000005, -7.47, -52.38, -20.74, 2.81, 75.43]                                #fallingr(78)


    # add all squares gradually
}

def move_safe(target_angles, lift=10):
    safe_angles = target_angles.copy()
    safe_angles[1] += lift

    safe_angles = clamp(safe_angles)
    target_angles = clamp(target_angles)

    # Step 1: SAFE
    mc.send_angles(safe_angles, SPEED)
    while True:
        current = mc.get_angles()
        if current and all(abs(c - s) < 5 for c, s in zip(current, safe_angles)):
            break
        time.sleep(1)

    # Step 2: TARGET
    mc.send_angles(target_angles, SPEED)
    while True:
        current = mc.get_angles()
        if current and all(abs(c - t) < 5 for c, t in zip(current, target_angles)):
            break
        time.sleep(0.1)

    return target_angles

def wait_until_reached(target, timeout=5, tol=4):
    start = time.time()

    while time.time() - start < timeout:
        curr = mc.get_angles()
        if curr and all(abs(c - t) < tol for c, t in zip(curr, target)):
            return True
        time.sleep(0.1)

    print("⚠️ Warning: target not fully reached")
    return False

def lift_current(lift=10):
    safe = current_angles.copy()
    safe[1] += lift
    safe = clamp(safe)

    mc.send_angles(safe, SPEED)
    wait_until_reached(safe)

    return safe

while True:
    #key = get_key()
    key = input("\nEnter command: ").strip()

    if key == 'x':
        print("\nExiting...")
        break

    if key == 'z':
        current_angles = [0,0,0,0,0,0]
        mc.send_angles(current_angles, SPEED)
        print("\nMoved to zero")
        continue
    
    if key == 'i':
        current_angles = [32.120000000000005, -7.47, -52.38, -20.74, 2.81, 75.43]
        mc.send_angles(current_angles, SPEED)
        print("\nMoved to initial position")
        continue

    if key == 'b':
        back_position = [32.120000000000005, -7.47, -52.38, -20.74, 2.81, 75.43]

        # Step 1: lift
        safe = lift_current(lift=10)

        # Step 2: go to back
        mc.send_angles(back_position, SPEED)
        wait_until_reached(back_position)

        current_angles = back_position

        print("\nMoved to back position (via safe)")
        continue

    # if key in position_map:
    #     current_angles = position_map[key]
    #     mc.send_angles(current_angles, SPEED)
    #     print(f"\nMoved to {key}")
    #     continue

    
    USE_SAFE = True

    if key in position_map:
        target = position_map[key]

        if USE_SAFE:
            current_angles = move_safe(target)
        else:
            current_angles = target
            mc.send_angles(current_angles, SPEED)

        print(f"\nMoved to {key}")
        continue

    # 🔥 GRIPPER CONTROL
    if key == 'o':
        mc.set_gripper_value(GRIP_OPEN, GRIP_SPEED)
        print("\nGripper OPEN")
        continue

    if key == 'c':
        mc.set_gripper_value(GRIP_CLOSE, GRIP_SPEED)
        print("\nGripper CLOSE")
        continue

    if key == 'p':
        mc.set_gripper_value(GRIP_OPEN_ZERO, GRIP_SPEED)
        print("\nGripper OPEN for zero position")
        continue

    if key in key_map:
        joint, delta = key_map[key]

        current_angles[joint] += delta
        current_angles = clamp(current_angles)

        mc.send_angles(current_angles, SPEED)
        print("\rAngles:", current_angles, end="")

    else:
        print("\nInvalid key")