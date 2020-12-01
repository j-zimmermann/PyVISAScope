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
import unicodedata
import logging
import sys


if sys.platform == 'linux':
    RESOURCE_MANAGER = visa.ResourceManager('@py')
elif sys.platform == 'win32':
    RESOURCE_MANAGER = visa.ResourceManager()

logger = logging.getLogger('pyvisa')


def get_resources():
    return RESOURCE_MANAGER.list_resources()


def convUnicodeToAscii(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


def getDeviceList():
    tmp = list(RESOURCE_MANAGER.list_resources())
    tmp = [convUnicodeToAscii(i) for i in tmp]
    return tmp


class scope(object):
    def __init__(self, resource):
        self.myScope = RESOURCE_MANAGER.open_resource(resource)
        self.mkdir = True
        self.counter = 0

    def checkChannel(self, channel):
        """ template for 4 channel oscilloscopes """
        answer = False
        if channel == 'CH1' or channel == 'CH2' or channel == 'CH3' or channel == 'CH4':
            answer = True
        if answer is False:
            logger.error('Choose one of the four channels, e.g. CH1')
            return answer
        return answer
