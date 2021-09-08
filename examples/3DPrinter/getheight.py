"""
Move needle down until surface is reached. Then, there will be a signal on the scope screen.
"""
import serial
import time
import numpy as np

ser = serial.Serial()
ser.baudrate = 115200
ser.port = "COM3"
ser.open()

# Home leveling X0 Y0 Z0
ser.write(b"G28\r\n")
ser.write(b"G1 Z25\r\n")
# flush buffer
time.sleep(2)
ser.flushInput()
ser.flushOutput()
time.sleep(0.5)
while True:
    ser.write(b"M114 D\r\n")
    time.sleep(1.0)
    response = ser.readline().decode("utf-8").rstrip()
    if "X:" not in response:
        continue
    else:
        coordinates = response.split(" ")[6:]
        x = float(coordinates[0].replace("X:", ""))
        y = float(coordinates[1].replace("Y:", ""))
        z = float(coordinates[2].replace("Z:", ""))
        if np.all(np.isclose([x, y, z], [0.0, 0.0, 25.15])):
            break

input("Move to origin! Make sure the chamber is NOT yet in position!\n Hit enter when ready!")
# move to new origin
ser.write(b"G1 X83,4 Y66,3 F700\r\n")
ser.write(b"G92 X0 Y0\r\n")
# wait until move finished
ser.write(b"M400\r\n")
time.sleep(2)
ser.flushInput()
ser.flushOutput()

while True:
    ser.write(b"M114 D\r\n")
    time.sleep(0.05)
    response = ser.readline().decode("utf-8").rstrip()
    if "X:" not in response:
        continue
    else:
        coordinates = response.split(" ")[0:3]
        x = float(coordinates[0].replace("X:", ""))
        y = float(coordinates[1].replace("Y:", ""))
        z = float(coordinates[2].replace("Z:", ""))
        if np.all(np.isclose([x, y, z], [0.0, 0.0, 25.0])):
            break

ser.write(b"M114 D\r\n")
response = ser.readline().decode("utf-8").rstrip()

# flush buffer
time.sleep(2)
ser.flushInput()
ser.flushOutput()
Z = 12
resolution = 0.1
input("Ready to move down?")
while True:
    ser.write(b"G1 Z%f\r\n" % Z)
    cmd = input("Enter 1 if step down, enter -1 to leave loop")
    if int(cmd) == 1:
        Z += -resolution
    else:
        break
    time.sleep(0.5)
print("Measured height (don't forget to subtract null level): ", Z)
