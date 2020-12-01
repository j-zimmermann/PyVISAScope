import pyvisa as visa
import pyvisascope
import logging

visa.log_to_screen('INFO')
logger = logging.getLogger('pyvisa')
log2file = logging.FileHandler('experiment.log')
logger.addHandler(log2file)


def main():
        # list the connected devices 
        print("Devices connected to your computer:")
        print(pyvisascope.get_resources())

if __name__ == '__main__':
        main()

