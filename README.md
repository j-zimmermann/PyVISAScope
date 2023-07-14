This small script is based on a [github repo](https://github.com/lab11/pyVisa_Tek_MSO2000) by Ye-Sheng Kuo. Thanks for giving me the permission to use and share your code!

Currently, this script works for Tektronix TDS2014B, RIGOL DS1000Z and SDS1104X-E scopes
and all scopes that share the same programming interface as the listed models.

# Requirements for windows users

* [NI-VISA](http://www.ni.com/de-de/support/downloads/drivers/download.ni-visa.html#306043)
* [pyVISA](https://pyvisa.readthedocs.io/en/master/)

# Requirements for linux users

* [pyVISA](https://pyvisa.readthedocs.io/en/latest/)
* [pyVISA-py](https://pyvisa-py.readthedocs.io/en/latest/)
* [pyUSB](http://pyusb.github.io/pyusb/)

# Additional requirements to run examples

* [multitimer](https://pypi.org/project/multitimer/)
* [pyYAML](https://pyyaml.org/)


# Troubleshooting for linux users
Give your device all rights you need to access it:
http://ask.xmodulo.com/change-usb-device-permission-linux.html

This solves this issue:
https://github.com/pyvisa/pyvisa/issues/212
