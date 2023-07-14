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
        # ID: 0x7ff3d88a3040
        Device = pyvisascope.RTB2004('USB0::0x0AAD::0x01D6::205123::INSTR')
        Device.myScope.timeout = 40000
        # set a timer that records every minute for in total 4 times
        # Device.set_wavegen()
        timer = multitimer.MultiTimer(interval=10, function=measure, kwargs={'myDevice': Device}, count=15, runonstart=True)
        timer.start()

        


def measure(myDevice):
        logger.info('Executing at {}'.format(time.ctime()))
        timestr = time.strftime('%Y%m%d-%H%M%S')
        waveform = myDevice.get_waveform(['CH1', 'CH2'])
        '''
        possible parameters for measurements are:
        FREQuency | PERiod | PEAK | UPEakvalue | LPEakvalue | PPCount | NPCount | 
        RECount | FECount | HIGH | LOW | AMPLitude | MEAN | RMS | RTIMe | FTIMe | 
        SRRise | SRFall | PDCYcle | NDCYcle | PPWidth | NPWidth | CYCMean | 
        CYCRms | STDDev | DELay | PHASe | DTOTrigger | CYCStddev | POVershoot | 
        NOVershoot | BWIDth
        for explanations look into the manual of the RTB2000
        '''        
        measurement = myDevice.get_measurement_series(['CH1', 'CH2'], ['PEAK', 'FREQ', 'RMS', 'MEAN', 'PHAS'], channel2="CH2")  # measure phase or delay against 2nd channel
        with open(timestr + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)
        with open(timestr + '-measurement.yml', 'w') as outfile:
                yaml.dump(measurement, outfile, default_flow_style=False)
        # myDevice.save_image()        

if __name__ == '__main__':
        main()