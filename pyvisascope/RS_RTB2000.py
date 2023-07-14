"""
    PyVISAScope provides an interface to different scopes.
    Copyright (C) 2016 Ye-Sheng Kuo <yesheng.kuo@gmail.com>
    Copyright (C) 2019 Julius Zimmermann <julius.zimmermann@uni-rostock.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import pyvisa as visa
import pyvisascope
import unicodedata
from .pyvisascope import scope, convUnicodeToAscii
import logging

logger = logging.getLogger('pyvisa')
'''
class WaveformFormat(object):
        def __init__(self, preambleString):
                preambleString = preambleString.replace('\n', '')
                tmp = preambleString.split(',')
                if len(tmp) == 5: # TODO
                        self.active = False
                        return
                self.active = True
                self.dictionary = {}
                self.dictionary['Time multiplier'] = float(tmp[4])
                logger.debug('Set time multiplier: {}'.format(self.dictionary['Time multiplier']))
                self.dictionary['Voltage multiplier'] = float(tmp[7])
                logger.debug('Set voltage multiplier: {}'.format(self.dictionary['Voltage multiplier']))
                self.dictionary['Voltage Offset'] = float(tmp[8]) + float(tmp[9])
                logger.debug('Set Voltage Offset: {}'.format(self.dictionary['Voltage Offset']))
                self.dictionary['Voltage Div'] = float(tmp[7])
                logger.debug('Set Voltage Div to {}'.format(self.dictionary['Voltage Div']))
                self.dictionary['Time Div'] = float(tmp[4])
                logger.debug('Set Time Div to {}'.format(self.dictionary['Time Div']))
'''



class RTB2004(scope):
        def __init__(self, resource):
                super().__init__(resource)

        def set_channel(self, channel):
                if self.checkChannel(channel):
                        self.myScope.write( 'SEARch:SOURce ' + channel)
                        logger.info('Set channel {}'.format(channel))
                else:
                        logger.error('Error format, ex: set_channel(\'CH1\')')
        
        def set_wavegen(self):
                self.myScope.write('*RST')
                self.myScope.write('WGEN:FUNC SIN') # Selects sine function
                self.myScope.write('WGEN:VOLT 700E-3') # Sets the amplitude
                self.myScope.write('WGEN:FREQ 1.00E+03') # Sets the frequency
                self.myScope.write('WGEN:OUTP:LOAD R50') # Sets the user load
                self.myScope.write('WGEN:OUTP 1') # Outputs the sine waveform
                self.myScope.write('AUT') # Autoscale to see the waveform

        def checkChannel(self, channel):
                """ template for 4 channel oscilloscopes """
                answer = False
                if channel == 'CH1' or channel == 'CH2' or channel == 'CH3' or channel == 'CH4':
                        answer = True
                if answer is False:
                        logger.error('Choose one of the four channels, e.g. CH1')
                        return answer
                return answer

        def get_channel(self):
                ch = convUnicodeToAscii(self.myScope.query( 'SEAR:SOUR' )).rstrip()
                logger.info('Current capture channel: {:}'.format(ch))
                return(ch)
        
        def get_version(self):
                idn = self.myScope.query('*IDN?')
                return(idn)       

        def acquire(self, start):
                if start == 'ON':
                        self.myScope.write('ACQuire:STATe RUN')
                elif start == 'OFF':
                        self.myScope.write('ACQuire:STATe STOP')
                else:
                        logger.error('Error format, ex: acquire(\'RUN/STOP\')')


        def get_measurement(self, channel, parameter, channel2=None):
                '''
                possible parameters are:
                FREQuency | PERiod | PEAK | UPEakvalue | LPEakvalue | PPCount | NPCount | 
                RECount | FECount | HIGH | LOW | AMPLitude | MEAN | RMS | RTIMe | FTIMe | 
                SRRise | SRFall | PDCYcle | NDCYcle | PPWidth | NPWidth | CYCMean | 
                CYCRms | STDDev | DELay | PHASe | DTOTrigger | CYCStddev | POVershoot | 
                NOVershoot | BWIDth
                for explanations look into the manual of the RTB2000
                '''
                if parameter == "PHAS":
                        if channel2 is None:
                                raise RuntimeError("For a phase measurement, you need to provide a 2nd channel!")
                        else:
                                self.checkChannel(channel2)
                        self.myScope.write('MEAS:SOUR ' + channel + ',' + channel2)
                        result = self.myScope.query('MEAS:RES? ' + parameter )
                else:
                        self.myScope.write('MEAS:SOUR ' + channel )
                        result = self.myScope.query('MEAS:RES? ' + parameter)
                return float(result)


        def get_measurement_series(self, channels, parameters, channel2=None):
            results = {}
            for channel in channels:
                if self.checkChannel(channel):
                    results[channel] = {}
                    for param in parameters:
                        results[channel][param] = self.get_measurement(channel, param, channel2)
            return results

        """
        def MKDIR(self, DIR):
            # start always from root
            self.myScope.write('FILESYSTEM:CWD "A:\\"')
            dirs = self.myScope.query('FILESYSTEM:DIR?').replace('\n', '')
            logger.debug(dirs)
            if DIR in dirs:
                logger.info('Measurement directory already exists')
                self.mkdir = False
            if self.mkdir is True:
                logger.info('Create new path for writing results')
                self.myScope.write('FILESYSTEM:MKDIR "A:\\' + DIR + '"')
                self.mkdir = False
            self.myScope.write('FILESYSTEM:CWD "A:\\' + DIR + '"')
            # set counter for files
            self.set_counter()
            self.DIR = 'A:\\' + DIR
            logger.debug('CWD: ' + self.myScope.query('FILESYSTEM:CWD?'))
            raise Exception('not implemented')
        
        def set_counter(self):
            files = self.myScope.query(':FILESYSTEM:DIR?').replace('"', '').replace('\n', '').split(',')
            logger.debug(files)
            files = [i for i in files if i.endswith('.SET')]
            files = [i.replace('.SET', '') for i in files]
            files = list(map(int, files))
            if len(files) > 0:
                self.counter = max(files) + 1
                logger.info('Start to write from index {}'.format(self.counter))
            raise Exception('not implemented')
            
                
        def save_all(self, channels, DIR='MEAS'):
            if len(DIR) > 8:
                raise Exception('Please check naming convention of the device. Not more than 8 characters are possible!')
            if self.counter == 0:
                self.MKDIR(DIR)
            self.filestr = self.DIR + '\\' + "{0:08d}".format(self.counter)
            self._save_setup()
            self._save_wave(channels)
            self.counter += 1
            raise Exception('not implemented')

        def _save_setup(self):
            logger.info('Saving setup')
            self.myScope.write(':SAVE:SETU "' + self.filestr + '.SET"')

        def _save_wave(self, channels, mode='USB'):
            logger.info('Saving waveform for {}'.format(channels))
            for channel in channels:
                if self.checkChannel(channel):
                    self.filestr = self.DIR + '\\' + channel + "{0:05d}".format(self.counter)
                    self.myScope.write(':SAVE:WAVEFORM ' + channel + ', "' + self.filestr + '.CSV"')


        """

        def get_waveform(self, channels):
                self.myScope.write('ACQuire:POINts 10000')
                self.myScope.write('*OPC')
                # stop acquisition
                self.acquire('OFF')
                waveform = {}
                for channel in channels:
                        if self.checkChannel(channel):
                                self.set_channel(channel)
                                if channel == 'CH1':
                                        channel_star = 'CHAN1'
                                if channel == 'CH2':
                                        channel_star = 'CHAN2'
                                if channel == 'CH3':
                                        channel_star = 'CHAN3'
                                if channel == 'CH4':
                                        channel_star = 'CHAN4'
                                preamble = self.myScope.query( channel_star + ':DATA:HEAD?' )
                                self.myScope.write('FORM ASC')
                                voltage_value = self.myScope.query(channel_star + ':DATA?')
                                time_value = []
                                t0 = self.myScope.query(channel_star + ':DATA:XORigin?')
                                time_increment = self.myScope.query('CHANnel2:DATA:XINCrement?')
                                voltage_value_list = list(map(float, voltage_value.split(',')))
                                for idx in range(0,len(voltage_value_list)):
                                        time_data = float(t0) + idx*float(time_increment)
                                        time_value.append(time_data)
                                waveform['time'] = time_value
                                waveform[channel] = voltage_value_list

                                '''
                                if preamble.active is False:
                                        logger.warning('Channel {} is not active'.format(channel))
                                        continue
                                # set reading mode to normal
                                self.myScope.write( ':WAV:MODE NORM' )
                                # set format to binary
                                self.myScope.write( ':FORM:DATA <REAL>' )
                                wave = self.myScope.query_binary_values( 'FORM:DATA <REAL>', datatype= 'B' )
                                voltage = [(i - preamble.dictionary['Voltage Offset']) * preamble.dictionary['Voltage multiplier']
                                           for i in wave]
                                if 'time' not in waveform:
                                        waveform['time'] = [i * preamble.dictionary['Time multiplier'] for i in range(len(voltage))]
                                waveform[channel] = voltage
                                '''
                        else:
                                logger.error('Error format, ex: get_waveform(\'CH1\')')
                                
                # restart acquisition
                self.acquire('ON')
                self.myScope.write('ACQuire:POINts:AUTomatic ON')
                self.myScope.write('*OPC')
                return waveform
        
        '''
        def save_image(self, counter=0):
            logger.info('Saving image')
            self.filestr = 'C:\\' + '{0:08d}'.format(self.counter)
            self.myScope.write(':SAVE:IMAge ' + self.filestr + '.png')
            self.counter += 1
        '''

        """
        def get_channel_position(self, channel):
                if self.checkChannel(channel):
                        self.set_channel(channel)
                        preamble = WaveformFormat(self.myScope.query(':WFMP?'))
                        pos = float(self.myScope.query(':' + channel + ':POS?'))
                        return preamble.dictionary['Voltage Div'] * pos
                else:
                        logger.error('Error format, ex: get_channel_position(\'CH1\')')

        def set_channel_position(self, channel, v):
                if self.checkChannel(channel):
                        self.set_channel(channel)
                        preamble = WaveformFormat(self.myScope.query(':WFMP?'))
                        self.myScope.write(':' + channel + ':POSition ' + str(float(v) / preamble.dictionary['Voltage Div']))
                else:
                        logger.error('Error format, ex: set_channel_position(\'CH1\', 0)')

        def get_volt_div(self, channel):
                if self.checkChannel(channel):
                        return float(convUnicodeToAscii(self.myScope.query(channel + ':SCA?')).rstrip())
                else:
                        logger.error('Error format, ex: get_volt_div(\'CH1\')')

        def set_volt_div(self, channel, v_div):
                if self.checkChannel(channel) and v_div in {0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50}:
                        self.myScope.write(channel + ':SCA ' + str(v_div))
                else:
                        logger.error('Error format, ex: set_volt_div(\'CH1\', 0.5)')
        """

