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
        # myDevice.set_recordlength('1e4') 
        '''Uncomment if you want to set always the same recordlength. 
        The possible values for recordlength are 
        1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6, 2e6, 5e6, 1e7, 2e7; see RTB2000 manual.
        If you want to set the value with the knobs on the oscilloscope, do not use this function.'''
        
        waveform = myDevice.get_waveform(['CH1', 'CH2'])
        #waveform = myDevice.get_waveform_downsampled(['CH1', 'CH2', 'CH3', 'CH4'],4) 
        #Downsample the waveform by the specified factor, here 4. In this example only every 4th sample will be saved. Choose either get_waveform or get_waveform_downsampled.
     
        measurement = myDevice.get_measurement_series(['CH1', 'CH2'], ['PEAK', 'FREQ', 'RMS', 'MEAN', 'PHAS'], channel2="CH2")  # measure phase or delay against channel2
        '''
        possible parameters for measurements are:
        FREQuency | PERiod | PEAK | UPEakvalue | LPEakvalue | PPCount | NPCount | 
        RECount | FECount | HIGH | LOW | AMPLitude | MEAN | RMS | RTIMe | FTIMe | 
        SRRise | SRFall | PDCYcle | NDCYcle | PPWidth | NPWidth | CYCMean | 
        CYCRms | STDDev | DELay | PHASe | DTOTrigger | CYCStddev | POVershoot | 
        NOVershoot | BWIDth
        for explanations look into the manual of the RTB2000
        '''  
        with open(timestr + '-wave.yml', 'w') as outfile:
                yaml.dump(waveform, outfile, default_flow_style=True)
        with open(timestr + '-measurement.yml', 'w') as outfile:
                yaml.dump(measurement, outfile, default_flow_style=False)
        # myDevice.save_image()        

if __name__ == '__main__':
        main()
