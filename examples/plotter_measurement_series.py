import yaml
import matplotlib.pyplot as plt
import os as os
from datetime import datetime


def main():
    listFiles = os.listdir('.')
    measurement = {}
    meas_value = []
    time_value = []
    for filename in listFiles:
        print(filename)
        if not filename.endswith('.yml'):
            continue 
        with open(filename) as f:
            meas = yaml.load(f)
        # Change below the desired channel and quantity! To select the desired channel use following abbreviations for the different oscilloscopes.
        # RIGOL DS1000Z series - 'CHAN1'; SIGLENT SDS1000x series - 'C1'; Tektronix TDS2000B series - 'CH1'
        meas_value.append(float(meas['CHAN1']['FREQ']))
        timestamp = filename.replace('-measurement.yml', '') 
        time_value.append(datetime.strptime(timestamp, '%Y%m%d-%H%M%S'))
                
    t, m = (list(t) for t in zip(*sorted(zip(time_value, meas_value))))
    measurement['time'] = [(x - t[0]).total_seconds() / 60. for x in t] 
    measurement['value'] = m

    plt.plot(measurement['time'], measurement['value'], 'g')
    #times = [x * 60 for x in range(len(measurement['value']))]
    #plt.plot(measurement['value'], 'r')
    plt.xlabel('time / min')
    plt.ylabel('frequency / Hz')
    plt.show()
    
if __name__ == '__main__':
    main()
