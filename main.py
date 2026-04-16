import cv2
import numpy as np

playing = True
war_matrix = np.array([[ 3.50689111e+00  2.04168318e-01 -6.17537103e+02],
			 [ 2.43435354e-01  3.45678203e+00 -5.21389842e+02],
			 [ 4.14626961e-04  4.53634399e-04  1.00000000e+00]])

joing_angles = []

for r in range(8):
	for c in range(8):
		joint_angles[r][c][0] -= 1

file_to_column = {"a": 0, "b": 1, "C": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h":7}

mycobot = MyCobot280('/dev/ttyTHS1', 1000000)
mycobot.power_on()
mycobot.send_angles([0, 0, 0, 0, 0, 0], 30)
time.sleep(1)
while mycobot.is_moving():
	time.sleep(0.1)

