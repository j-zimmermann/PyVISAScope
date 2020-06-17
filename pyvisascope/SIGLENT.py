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


class SIGLENT(scope):
        def __init__(self, resource):
                super().__init__(resource)

        def set_channel(self, channel):
                if self.checkChannel(channel):
                        self.myScope.write('DATa:SOUrce ' + channel)
                        logger.info('Set channel {}'.format(channel))
                else:
                        logger.error('Error format, ex: set_channel(\'CH1\')')

        def get_channel(self):
                ch = convUnicodeToAscii(self.myScope.query(':DAT:SOU?')).rstrip()
                logger.info('Current capture channel: {:}'.format(ch))
                return(ch)

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

        def get_waveform(self):
                self.myScope.write("chdr off")
                vdiv = self.myScope.query("c1:vdiv?")
                ofst = self.myScope.query("c1:ofst?")
                tdiv = self.myScope.query("tdiv?")
                sara = self.myScope.query("sara?") #sara - samplerate
                sara = float(sara)
                print('samplerate = ', sara,' Hz')
                print(type(sara))
                self.myScope.timeout=30000
                #self.myScope.chunk_size = 20*1024*1024
                self.myScope.write('C1:WF? DAT2')
                #print(resp)
                #print(type(resp))
                print('000')
                recv = list(self.myScope.read_bytes(1))[15:]
                print('001')
                recv.pop()
                recv.pop()
                volt_value=[]
                for data in recv:
                    if data > 127:
                        data = data -255
                    else:
                        pass
                    volt_value.append(data)
                time_value = []
                '''
                for idx in range(0,len(volt_value)):
                    volt_value[idx] = volt_value[idx]/25*float(vdiv)-float(ofst)
                    time_data = -(float(tdiv)*14/2)+idx*(1/sara)
                    time_value.append(time_data)
                    pl.figure(figsize=(7,5))
                    pl.plot(time_value,volt_value,markersize=2,label=u"Y-T")
                    pl.legend()
                    pl.grid()
                    pl.show()
                '''
 
        def get_version(self):
                self.myScope.query('*IDN?')

        def get_number_of_datapoints(self):
                print(self.myScope.query('SANU? C1'))

                
'''
        def waveform(self, outfile, channel):
                self.myScope.timeout = 120000
                sample_rate = self.myScope.query('SANU C%d?' % channel)

                sample_rate = int(sample_rate[len('SANU '):-2])
                logger.info('detected sample rate of %d' % sample_rate)

                #desc = device.write('C%d: WF? DESC' % channel)
                #logger.info(repr(device.read_raw()))

                # the response to this is binary data so we need to write() and then read_raw()
                # to avoid encode() call and relative UnicodeError
                logger.info(self.myScope.write('C%d: WF? DAT2' % (channel,))) 

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
                CRM, CURSORRM, DEL, FALL, FREQ, MAXI, MEAN, MINI, NONE, NWI, PDU, PERI, PHA, PK2PK, PWI, RIS
                """
                self.myScope.write(':MEASU:IMMED:SOU ' + channel)
                self.myScope.write(':MEASU:IMMED:TYP ' + parameter)
                result = self.myScope.query(':MEASU:IMMED:VAL?')
                return float(result)

        def get_measurement_series(self, channels, parameters):
            results = {}
            for channel in channels:
                if self.checkChannel(channel):
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

        def get_waveform(self, channels):
                # stop acquisition
                self.acquire('OFF')
                waveform = {}
                for channel in channels:
                        if self.checkChannel(channel):
                                self.set_channel(channel)
                                preamble = WaveformFormat(self.myScope.query(':WFMP?'))
                                if preamble.active is False:
                                        logger.warning('Channel {} is not active'.format(channel))
                                        continue
                                wave = self.myScope.query_binary_values(':CURV?', datatype='B')
                                voltage = [(i - preamble.dictionary['Voltage Offset']) * preamble.dictionary['Voltage multiplier']
                                           for i in wave]
                                if 'time' not in waveform:
                                        waveform['time'] = [i * preamble.dictionary['Time multiplier'] for i in range(len(voltage))]
                                waveform[channel] = voltage
                        else:
                                logger.error('Error format, ex: get_waveform(\'CH1\')')
                # restart acquisition
                self.acquire('ON')
                return waveform

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

'''
