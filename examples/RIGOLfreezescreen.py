import pyvisa as visa
import pyvisascope
import multitimer
import time
import yaml
import logging
from time import sleep

visa.log_to_screen('INFO')
logger = logging.getLogger('pyvisa')
log2file = logging.FileHandler('experiment.log')
logger.addHandler(log2file)


def main():
        # enter here the ID of your device. On windows, VISA you can easily find it in the VISA interface.
        Device = pyvisascope.MSO5000('USB::0x1AB1::0x0515::MS5A230800492::INSTR')
        Device.myScope.timeout = None
        # set a timer that records every minute for in total 4 times
        timer = multitimer.MultiTimer(interval=20, function=measure, kwargs={'myDevice': Device}, count=3, runonstart=True)
        timer.start()


def measure(myDevice):
        logger.info('Executing at {}'.format(time.ctime()))
        timestr = time.strftime('%Y%m%d-%H%M%S')
        # sleep 3 seconds
        sleep(3)
        # freeze screen
        myDevice.acquire("OFF")
        waveform = myDevice.get_waveform(['CHAN1', 'CHAN2', 'CHAN3'], autofreeze=False)
        # further measurement parameters and the needed abbreviation can be found in ds1000z_programming guide
        measurement = myDevice.get_measurement_series(['CHAN1', 'CHAN2', 'CHAN3'], ['VPP', 'Vavg', 'FREQ', 'VRMS', 'RRPH'], channel2=["CHAN1"])  # measure phase against 2nd channel
        # unfreeze screen
        myDevice.acquire("ON")
        with open(timestr + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)
        with open(timestr + '-measurement.yml', 'w') as outfile:
                yaml.dump(measurement, outfile, default_flow_style=False)


if __name__ == '__main__':
        main()
