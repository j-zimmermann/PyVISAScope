import pyvisa as visa
import pyvisascope
import multitimer
import time
import yaml
import logging

visa.log_to_screen('INFO')
logger = logging.getLogger('pyvisa')
log2file = logging.FileHandler('experiment.log')
logger.addHandler(log2file)


def main():
        # enter here the ID of your device. On windows, VISA you can easily find it in the VISA interface.
        Device = pyvisascope.SDS_1104X_E('USB0::62700::60984::SDSMMEBD2R5477::0::INSTR')
        Device.myScope.timeout = None
        # set a timer that records every minute for in total 4 times
        #timer = multitimer.MultiTimer(interval=5, function=measure, kwargs={'myDevice': Device}, count=10, runonstart=True)
        timer = multitimer.MultiTimer(interval=60, function=measure, kwargs={'myDevice': Device}, count=1440, runonstart=True)
        timer.start()


def measure(myDevice):
        logger.info('Executing at {}'.format(time.ctime()))
        timestr = time.strftime('%Y%m%d-%H%M%S')
        waveform = myDevice.get_waveform(['C1'])
        measurement = myDevice.get_measurement_series(['C1'], ['PKPK', 'MEAN', 'FREQ'])
        with open(timestr + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)
        with open(timestr + '-measurement.yml', 'w') as outfile:
                yaml.dump(measurement, outfile, default_flow_style=False)


if __name__ == '__main__':
        main()
