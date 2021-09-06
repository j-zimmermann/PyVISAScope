import serial
ser = serial.Serial()
ser.baudrate = 115200
ser.port = "COM3"
ser.open()
ser.write(b"G1 Z25\r\n")
