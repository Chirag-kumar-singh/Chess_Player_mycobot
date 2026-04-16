from pymycobot.mycobot import MyCobot
import time

# ---------------- CONFIG ----------------
PORT = "/dev/ttyTHS1"     # Jetson Nano UART
BAUD = 1000000            # myCobot 280 JN baudrate
SPEED = 20                # Safe speed (0–100)
# ----------------------------------------

def main():
    print("Connecting to myCobot...")
    mc = MyCobot(PORT, BAUD)
    time.sleep(1)

    print("Powering on robot...")
    mc.power_on()
    time.sleep(1)

    print("Enabling fresh mode...")
    mc.set_fresh_mode(1)
    time.sleep(0.5)

    print("Moving to ZERO position (all joints = 0°)...")
    mc.send_angles([32.120000000000005, -7.47, -52.38, -20.74, 2.81, 75.43], SPEED)

    # Wait until motion completes
    while mc.is_moving():
        time.sleep(0.1)

    print("✅ Robot reached ZERO position safely.")

    mc.close()


if __name__ == "__main__":
    main()


