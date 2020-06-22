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

'''
class WaveformFormat(object):
        def __init__(self, preambleString):
                preambleString = preambleString.replace('\n', '')
                tmp = preambleString.split(';')
                if len(tmp) == 5:
                        self.active = False
                        return
                self.active = True
                self.dictionary = {}
                for i in range(len(tmp)):
                        if tmp[i] == '"s"':
                                self.dictionary['Time multiplier'] = float(tmp[i - 3])
                                logger.debug('Set time multiplier: {}'.format(self.dictionary['Time multiplier']))
                        elif tmp[i] == '"Volts"':
                                self.dictionary['Voltage multiplier'] = float(tmp[i - 3])
                                logger.debug('Set voltage multiplier: {}'.format(self.dictionary['Voltage multiplier']))
                                self.dictionary['Voltage Offset'] = float(tmp[i - 1])
                                logger.debug('Set Voltage Offset: {}'.format(self.dictionary['Voltage Offset']))
                        elif 'Ch' in tmp[i]:
                                self.channel_info = tmp[i].split(',')
                                logger.debug('Channel info:')
                                logger.debug(self.channel_info)
                                self.dictionary['Voltage Div'] = float(self.channel_info[2].replace('V/div', '').rstrip())
                                logger.debug('Set Voltage Div to {}'.format(self.dictionary['Voltage Div']))
                                self.dictionary['Time Div'] = float(self.channel_info[3].replace('s/div', '').rstrip())
                                logger.debug('Set Time Div to {}'.format(self.dictionary['Time Div']))
                self.dictionary['Time multiplier'] = self.query('tdiv?')
                logger.debug('Set time multiplier: {}'.format(self.dictionary['Time multiplier']))
                self.dictionary['Voltage multiplier'] = self.query('vdiv?')
                logger.debug('Set voltage multiplier: {}'.format(self.dictionary['Voltage multiplier']))
                self.dictionary['Voltage Offset'] = self.query('ofst?')
                logger.debug('Set Voltage Offset: {}'.format(self.dictionary['Voltage Offset']))
                self.dictionary['Voltage Div'] = self.query('vdiv?')
                logger.debug('Set Voltage Div to {}'.format(self.dictionary['Voltage Div']))
                self.dictionary['Time Div'] = self.query('tdiv?')
                logger.debug('Set Time Div to {}'.format(self.dictionary['Time Div']))
'''

class SDS_1104X_E(scope):
        #def __init__(self, resource):
                #super().__init__(resource)

        def set_channel(self, channel):
                if self.checkChannel(channel):
                        self.myScope.query(channel + ':trace')
                        logger.info('Set channel {}'.format(channel))
                else:
                        logger.error('Error format, ex: set_channel(\'CH1\')')

        def get_channel(self):
                ch = convUnicodeToAscii(self.myScope.query(':DAT:SOU?')).rstrip()
                logger.info('Current capture channel: {:}'.format(ch))
                return(ch)

        def check_channel(self, channel):
                """ template for 4 channel oscilloscopes """
                answer = False
                if channel == 'C1' or channel == 'C2' or channel == 'C3' or channel == 'C4':
                        answer = True
                if answer is False:
                        logger.error('Choose one of the four channels, e.g. C1')
                        return answer
                return answer

        def acquire(self, start):
                if start == 'ON':
                        self.myScope.write(':ARM')
                elif start == 'OFF':
                        self.myScope.write(':STOP')
                else:
                        logger.error('Error format, ex: acquire(\'ON/OFF\')')

        def get_state(self):
                print(self.myScope.query(':INR?'))
                
        def get_aqw_status(self):
                print(self.myScope.query(':SAST?'))
                
        def set_time_div(self, time):
                self.myScope.write('TIME_DIV ' + time)
                print(self.myScope.query('TIME_DIV?'))

        def cal(self):
                self.myScope.write('*CAL?')

        
        def get_waveform(self, channels):
                self.myScope.write("chdr off")
                waveform = {}
                sara = self.myScope.query("sara?") #sara - samplerate
                sara = float(sara)
                self.myScope.timeout=30000
                self.myScope.chunk_size = 20*1024*1024
                for channel in channels:
                        if self.check_channel(channel):
                                vdiv = self.myScope.query(channel + ":vdiv?")
                                ofst = self.myScope.query(channel + ":ofst?")
                                tdiv = self.myScope.query("tdiv?")
                                self.myScope.write(channel + ':WF? DAT2')
                                recv = list(self.myScope.read_raw())[15:]
                                recv.pop()
                                recv.pop()
                                volt_value = []
                                for data in recv:
                                    if data > 127:
                                        data = data - 255
                                    else:
                                        pass
                                    volt_value.append(data)
                                time_value = []                
                                for idx in range(0,len(volt_value)):
                                        volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
                                        time_data = -(float(tdiv)*14/2)+idx*(1/sara)
                                        time_value.append(time_data)
                                waveform['time'] = time_value
                                waveform[channel] = volt_value
                return waveform    

        def get_version(self):
                self.myScope.query('*IDN?')

        def get_number_of_datapoints(self):
                print(self.myScope.query('SANU? C1'))

                
        def waveform(self, outfile, channel):
                self.myScope.timeout = 120000
                sample_rate = self.myScope.query('SANU? C%d' % channel)

                sample_rate = int(sample_rate[len('SANU '):-2])
                logger.info('detected sample rate of %d' % sample_rate)

                #desc = device.write('C%d: WF? DESC' % channel)
                #logger.info(repr(device.read_raw()))

                # the response to this is binary data so we need to write() and then read_raw()
                # to avoid encode() call and relative UnicodeError
                logger.info(self.myScope.write('C%d:WF? DAT2' % (channel,))) 

                response = self.myScope.read_raw()

                if not response.startswith('C%d:WF ALL' % channel):
                    raise ValueError('error: bad waveform detected -> \'%s\'' % repr(response[:80]))

                index = response.index('#9')
                index_start_data = index + 2 + 9
                data_size = int(response[index + 2:index_start_data])
                # the reponse terminates with the sequence '\n\n\x00' so
                # is a bit longer that the header + data
                data = response[index_start_data:index_start_data + data_size]
                logger.info('data size: %d' % data_size)

                fd = wave.open(outfile, "w")
                fd.setparams((
                 1,               # nchannels
                 1,               # sampwidth
                 sample_rate,     # framerate
                 data_size,       # nframes
                 "NONE",          # comptype
                 "not compresse", # compname
                ))
                fd.writeframes(data)
                fd.close()

                logger.info('saved wave file')

        def get_measurement(self, channel, parameter):
                """
                possible parameters are:
                PKPK, MAX, MIN, AMPL, TOP, BASE, CMEAN, MEAN, RMS, CRMS, OVSN, FPRE, OVSP, RPRE, PER, FREQ, PWID, NWID, RISE, FALL, WID, DUTY, NDUTY, ALL
                """
                self.myScope.write('PACU' + parameter +',' + channel)
                result = self.myScope.query(channel +':PAVA? ' + parameter)
                result = result.split(',')
                result[1] = result[1].replace('\n','')
                if result[1] == '****':
                        result[1] = '0'
                result = float(result[1])
                return result

        def get_measurement_series(self, channels, parameters):
            results = {}
            for channel in channels:
                if self.check_channel(channel):
                    results[channel] = {}
                    for param in parameters:
                        results[channel][param] = self.get_measurement(channel, param)
            return results

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

        def set_counter(self):
            files = self.myScope.query(':FILESYSTEM:DIR?').replace('"', '').replace('\n', '').split(',')
            logger.debug(files)
            files = [i for i in files if i.endswith('.SET')]
            files = [i.replace('.SET', '') for i in files]
            files = list(map(int, files))
            if len(files) > 0:
                self.counter = max(files) + 1
                logger.info('Start to write from index {}'.format(self.counter))

        def save_all(self, channels, DIR='MEAS'):
            if len(DIR) > 8:
                raise Exception('Please check naming convention of the device. Not more than 8 characters are possible!')
            if self.counter == 0:
                self.MKDIR(DIR)
            self.filestr = self.DIR + '\\' + "{0:08d}".format(self.counter)
            self._save_setup()
            self._save_wave(channels)
            self.counter += 1

        def _save_setup(self):
            logger.info('Saving setup')
            self.myScope.write(':SAVE:SETU "' + self.filestr + '.SET"')

        def _save_wave(self, channels, mode='USB'):
            logger.info('Saving waveform for {}'.format(channels))
            for channel in channels:
                if self.checkChannel(channel):
                    self.filestr = self.DIR + '\\' + channel + "{0:05d}".format(self.counter)
                    self.myScope.write(':SAVE:WAVEFORM ' + channel + ', "' + self.filestr + '.CSV"')
        '''
        def get_waveform(self, channels):
                # stop acquisition
                print('getwaveform gestartet')
                #self.acquire('OFF')
                self.myScope.chunk_size = 20*1024*1024
                waveform = {}
                for channel in channels:
                        if self.checkChannel(channel):
                                self.set_channel(channel)
                                preamble = WaveformFormat(self.myScope.query('WFSU?'))
                                if preamble.active is False:
                                        logger.warning('Channel {} is not active'.format(channel))
                                        continue
                                print(preamble)
                                self.myScope.write('C1:WF? DAT2')
                                #wave = self.myScope.query_binary_values(':WF?', datatype='B')
                                wave = list(self.myScope.read_raw())[15:]
                                wave.pop()
                                wave.pop()
                                print('waveform gelesen')
                                voltage = [(i - preamble.dictionary['Voltage Offset']) * preamble.dictionary['Voltage multiplier']
                                           for i in wave]
                                if 'time' not in waveform:
                                        waveform['time'] = [i * preamble.dictionary['Time multiplier'] for i in range(len(voltage))]
                                waveform[channel] = voltage
                        else:
                                logger.error('Error format, ex: get_waveform(\'CH1\')')
                # restart acquisition
                self.acquire('ON')
                print('getwaveform beendet')
                return waveform
        '''

        def get_channel_position(self, channel):
                if self.checkChannel(channel):
                        self.set_channel(channel)
                        preamble = WaveformFormat(self.myScope.query('WFSU?'))
                        pos = float(self.myScope.query(channel + ':OFST?'))
                        return preamble.dictionary['Voltage Div'] * pos
                else:
                        logger.error('Error format, ex: get_channel_position(\'CH1\')')

        def set_channel_position(self, channel, v):
                if self.check_channel(channel):
                        self.set_channel(channel)
                        preamble = WaveformFormat(self.myScope.query('WFSU?'))
                        self.myScope.write(channel + ':OFST ' + str(float(v) / preamble.dictionary['Voltage Div']))
                else:
                        logger.error('Error format, ex: set_channel_position(\'CH1\', 0)')

        def get_volt_div(self, channel):
                if self.checkChannel(channel):
                        return float(convUnicodeToAscii(self.myScope.query(channel + 'VOLT_DIV?')).rstrip())
                else:
                        logger.error('Error format, ex: get_volt_div(\'CH1\')')

        def set_volt_div(self, channel, v_div):
                if self.checkChannel(channel) and v_div in {0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50}:
                        self.myScope.write(channel + 'VOLT_DIV ' + str(v_div))
                else:
                        logger.error('Error format, ex: set_volt_div(\'CH1\', 0.5)')
