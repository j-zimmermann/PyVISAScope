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
        Device = pyvisascope.SIGLENT('USB0::62700::60984::SDSMMEBD2R5477::0::INSTR')
#        Device.get_version()
        Device.get_state()
        Device.get_state()
        Device.get_aqw_status()
        Device.set_time_div('200US')
        # set horizontal scale per division for the main window: NS - nanoseconds, US - microsecond, MS - milliseconds, s - seconds
        # Device.acquire("ON")
        time.sleep(2)
        Device.get_number_of_datapoints()
#        Device.waveform('test.out', 1)
#        Device.acquire("OFF")
#        time.sleep(10)
#        Device.timeout = 15000
        Device.get_waveform()
        Device.get_state()
        #Device.myScope.timeout = None
        # set a timer that records every 10s for in total 4 times
        #timer = multitimer.MultiTimer(interval=10, function=measure, kwargs={'myDevice': Device}, count=3, runonstart=True)
        #timer.start()


def measure(myDevice):
        logger.info('Executing at {}'.format(time.ctime()))
        timestr = time.strftime('%Y%m%d-%H%M%S')
        waveform = myDevice.get_waveform(['CH1', 'CH2', 'CH3', 'CH4'])
        measurement = myDevice.get_measurement_series(['CH1', 'CH2', 'CH3', 'CH4'], ['PK2', 'MEAN', 'FREQ'])
        with open(timestr + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)
        with open(timestr + '-measurement.yml', 'w') as outfile:
                yaml.dump(measurement, outfile, default_flow_style=False)


if __name__ == '__main__':
        main()
