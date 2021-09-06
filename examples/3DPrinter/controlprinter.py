import time
import serial
import numpy as np
import logging
import yaml
import pyvisa as visa
import pyvisascope
from grid import get_grid
import os

if not os.path.exists("data"):
    os.makedirs("data")

if os.path.exists('experiment.log'):
    os.remove('experiment.log')


visa.log_to_screen('INFO')
logger = logging.getLogger('pyvisa')
log2file = logging.FileHandler('experiment.log')
logger.addHandler(log2file)

sleepingtime = 2


def move_printer(serialconnection, X, Y, Z):
        logger.info("Position: {}, {}, {}".format(X, Y, Z))
        # move 3d printer
        serialconnection.write(b"G1 X%f Y%f Z%f\r\n" % (X, Y, Z))
        time.sleep(0.5)
        # flush buffer
        serialconnection.flushInput()
        serialconnection.flushOutput()
        # to check if it stopped moving
        xlast = 0.0
        ylast = 0.0
        zlast = 0.0
        while True:
            # get position
            serialconnection.write(b"M114 D\r\n")
            # time to get answer
            time.sleep(0.25)
            response = serialconnection.readline().decode("utf-8").rstrip()
            logger.info("Response to M114: {}".format(response))
            # log responses until position does not change any more
            if "X:" not in response:
                continue
            else:
                coordinates = response.split(" ")[6:]
                logger.info(coordinates)
                x = float(coordinates[0].replace("X:", ""))
                y = float(coordinates[1].replace("Y:", ""))
                z = float(coordinates[2].replace("Z:", ""))
                if np.all(np.isclose([x, y, z], [xlast, ylast, zlast])):
                    break
                else:
                    xlast = x
                    ylast = y
                    zlast = z
        # switch off engine
        serialconnection.write(b"M18\r\n")
        return


def main(grid):
        # connect to scope
        # enter here the ID of your device. On windows, VISA you can easily find it in the VISA interface.
        Device = pyvisascope.MSO5000('USB::0x1AB1::0x0515::MS5A230800492::INSTR')
        Device.myScope.timeout = None

        # connect to 3D printer
        ser = serial.Serial()
        ser.baudrate = 115200
        # choose right port
        ser.port = "COM3"
        # timeout needed?
        ser.timeout = 5
        # open connection and wait
        ser.open()
        print(ser.is_open)
        time.sleep(2)
        # flush buffer
        ser.flushInput()
        ser.flushOutput()

        # stop reporting temperature
        ser.write(b"M155 S0\r\n")
        input("Home leveling!  Make sure the chamber is NOT yet in position!\n Hit enter when ready!")
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
            logger.info(response)
            if "X:" not in response:
                continue
            else:
                coordinates = response.split(" ")[6:]
                logger.info(coordinates)
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
            logger.info("Loop resp.: {}".format(response))
            if "X:" not in response:
                continue
            else:
                coordinates = response.split(" ")[0:3]
                logger.info(coordinates)
                x = float(coordinates[0].replace("X:", ""))
                y = float(coordinates[1].replace("Y:", ""))
                z = float(coordinates[2].replace("Z:", ""))
                if np.all(np.isclose([x, y, z], [0.0, 0.0, 25.0])):
                    break

        ser.write(b"M114 D\r\n")
        response = ser.readline().decode("utf-8").rstrip()
        logger.info("After loop resp.: {}".format(response))

        # flush buffer
        time.sleep(2)
        ser.flushInput()
        ser.flushOutput()

        input("Move along grid. Make sure chamber is in position!")
        # move along grid
        for i, g in enumerate(grid):
            move_printer(ser, g[0], g[1], g[2])
            # take measurement
            measure(Device, i)
        ser.write(b"G1 Z25\r\n")
        ser.close()
        print("Remove chamber, experiment done")


def measure(myDevice, idx):
        # to record data from oscilloscope
        logger.info('Executing at {}'.format(time.ctime()))
        # sleep X seconds to wait for stable signal
        time.sleep(sleepingtime)
        # freeze screen
        myDevice.acquire("OFF")
        waveform = myDevice.get_waveform(['CHAN1', 'CHAN2', 'CHAN3'], autofreeze=False)
        # unfreeze screen
        myDevice.acquire("ON")
        with open("data/" + str(idx) + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)


def plot_grid(grid):
        x = list(zip(*grid))[0]
        y = list(zip(*grid))[1]
        z = list(zip(*grid))[2]
        import matplotlib.pyplot as plt
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        ax.scatter(x, y, z, marker='o')
        plt.show()


if __name__ == '__main__':
        grid = get_grid()
        plot_grid(grid)
        main(grid)
