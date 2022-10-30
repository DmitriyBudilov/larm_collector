from datetime import datetime as dt
from .Py3E24lib import PyE24lib
from .config import parameters

def read_value_from_ttyUSB(E24_config):
    value = E24_config.read_value_ADC()
    convert_string = '{:%H:%M:%S.%f}'.format(value['datetime']) + ' ' + str(value['channel']) + ' ' + str(int(value['value']))
    return convert_string

if __name__ == '__main__':
    E24 = PyE24lib(parameters)
    while True:
        print(read_value_from_ttyUSB(E24))
