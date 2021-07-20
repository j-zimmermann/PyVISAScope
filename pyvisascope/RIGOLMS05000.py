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


from .pyvisascope import scope, convUnicodeToAscii
import logging

logger = logging.getLogger('pyvisa')


class WaveformFormat(object):
        def __init__(self, preambleString):
                preambleString = preambleString.replace('\n', '')
                tmp = preambleString.split(',')
                if len(tmp) == 5:  # TODO
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


class MSO5000(scope):
        def __init__(self, resource):
                super().__init__(resource)

        def set_channel(self, channel):
                if self.checkChannel(channel):
                        self.myScope.write('WAV:SOUR ' + channel)
                        logger.info('Set channel {}'.format(channel))
                else:
                        logger.error('Error format, ex: set_channel(\'CHAN1\')')

        def checkChannel(self, channel):
                """ template for 4 channel oscilloscopes """
                answer = False
                if channel == 'CHAN1' or channel == 'CHAN2' or channel == 'CHAN3' or channel == 'CHAN4':
                        answer = True
                if answer is False:
                        logger.error('Choose one of the four channels, e.g. CHAN1')
                        return answer
                return answer

        def get_channel(self):
                ch = convUnicodeToAscii(self.myScope.query(':WAV:SOUR?')).rstrip()
                logger.info('Current capture channel: {:}'.format(ch))
                return(ch)

        def acquire(self, start):
                if start == 'ON':
                        self.myScope.write(':RUN')
                        logger.info('Start acquisition')
                elif start == 'OFF':
                        self.myScope.write(':STOP')
                        logger.info('Stop acquisition')
                else:
                        logger.error('Error format, ex: acquire(\'RUN/STOP\')')

        def get_measurement(self, channel, parameter, channel2=None):
                '''
                possible parameters are:
                Vmax, Vmin, Vpp, Vtop, Vbase, Vamp, Vavg, Vrms, Overshoot, Preshoot, RRPHase
                '''
                if parameter == "RRPHase":
                    if channel2 is None:
                        raise RuntimeError("For a phase measurement, you need to provide a 2nd channel!")
                    else:
                        self.checkChannel(channel2)
                    self.myScope.write(':MEAS:ITEM ' + parameter + ',' + channel + ',' + channel2)
                    result = self.myScope.query(':MEAS:ITEM? ' + parameter + ',' + channel + ',' + channel2)
                else:
                    self.myScope.write(':MEAS:ITEM ' + parameter + ',' + channel)
                    result = self.myScope.query(':MEAS:ITEM? ' + parameter + ',' + channel)
                return float(result)

        def get_measurement_series(self, channels, parameters, channel2=None):
            results = {}
            for channel in channels:
                if self.checkChannel(channel):
                    results[channel] = {}
                    for param in parameters:
                        results[channel][param] = self.get_measurement(channel, param, channel2)
            return results

        def save_image(self, counter=0):
            logger.info('Saving image')
            self.filestr = 'D:\\' + '{0:08d}'.format(self.counter)
            self.myScope.write(':SAVE:IMAge ' + self.filestr + '.png')
            self.counter += 1

        def get_waveform(self, channels, autofreeze=True):
                # stop acquisition
                if autofreeze:
                    self.acquire('OFF')
                waveform = {}
                for channel in channels:
                        if self.checkChannel(channel):
                                self.set_channel(channel)
                                preamble = WaveformFormat(self.myScope.query(':WAV:PRE?'))
                                if preamble.active is False:
                                        logger.warning('Channel {} is not active'.format(channel))
                                        continue
                                # set reading mode to normal
                                self.myScope.write(':WAV:MODE NORM')
                                # set format to binary
                                self.myScope.write(':WAV:FORM BYTE')
                                wave = self.myScope.query_binary_values(':WAV:DATA?', datatype='B')
                                voltage = [(i - preamble.dictionary['Voltage Offset']) * preamble.dictionary['Voltage multiplier']
                                           for i in wave]
                                if 'time' not in waveform:
                                        waveform['time'] = [i * preamble.dictionary['Time multiplier'] for i in range(len(voltage))]
                                waveform[channel] = voltage
                        else:
                                logger.error('Error format, ex: get_waveform(\'CH1\')')
                # restart acquisition
                if autofreeze:
                    self.acquire('ON')
                return waveform
