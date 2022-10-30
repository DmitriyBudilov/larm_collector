#!/usr/bin/python
# -*- coding: utf-8 -*-

# PyE24lib.py it's a high level module/library for working with ADC E24 by L-Card company.
# For more information about hardware, visit http://www.lcard.ru,
# Remember, channels number start from 1 (as human readable, not computer).
#
# Author: Makhmudov Evgeniy aka JOHN_16 <john_16@list.ru>
#
# If you find bugs, have comments or questions, or may be want donating author send message by e-mail.
#
# License GPL ver.2
#
# Example for using in your code:
#
# from PyE24lib import PyE24lib
#
# # Prepare dictionary to send in constructor of PyE24lib class
# parameters={'port': '/dev/ttyUSB0',            # COM port which attached device
#             'five_byte_mode': True,            # Enable internal timer
#             'channels': {                      # Internal dictionary which describes channels parameters
#                          1: {                  # Enable channel 1
#                              'frequency': 100, # Set frequency to 100Hz
#                              'input_type': 0,  # Set channel input to Line A
#                              'gain': 1,        # Set Gain level to one
#                              'calibration': 0  # Disable any calibration
#                              }
#                         }
# # Make instance of class and send him dictionary with parameters
# E24=PyE24lib(parameters)
#
# # Read from ADC 5 values
# values=[E24.read_value_ADC() for x in xrange(5)]
#
# # Print values
# for item in values:
#     print E24.value_to_string(item)
#
# # Close port
# E24.close()

__VERSION__='0.1.5'

import traceback, struct, datetime, time, pdb

import serial

class PyE24lib(object):
    """The main class. All ways start here"""

    def __init__(self, config_dict):
        self.config=config_dict

        self.serial=serial.Serial(config_dict['port'],
                                  config_dict.get('baudrate', 19200),
                                  bytesize=serial.EIGHTBITS,
                                  stopbits=serial.STOPBITS_ONE,
                                  parity=serial.PARITY_NONE,
                                  timeout=config_dict.get('timeout', 1))

        self.active_channels=0b0000
        self.byte_mode=4

        self._koefficient=2500.0/(2**23) if int(config_dict.get('output_in_mv', 0)) else 1

        # according to the documentation
        self.serial.setDTR(False)
        self.serial.setRTS(True)

        if 'channels' in config_dict:
            self.first_initialize(config_dict)

    def first_initialize(self, params):
        """ Initialize ADC parameters. After this, ADC prepare to working"""

        self.stop()
        self.set_active_channels(1 in params['channels'],
                                 2 in params['channels'],
                                 3 in params['channels'],
                                 4 in params['channels'])
        self.stop()

        for i in range(4):
            if (self.active_channels&(0b1<<i))>>i:
                self.set_channel_frequency(i+1, params['channels'][i+1]['frequency'])
                self.set_gain_and_calibration(i+1, params['channels'][i+1]['gain'], params['channels'][i+1]['calibration'])
                self.set_channel_input_type(i+1, params['channels'][i+1]['input_type'])
        if params.get('five_byte_mode'):
            self.set_byte_mode(5)

        self.reinitialization()


    def toADC(self, *args):
        """Send byte arguments to ADC"""
        value=struct.pack('B'*len(args), *args)
        result=self.serial.write(value)
        self.serial.flushInput()
        time.sleep(0.1)
        return result,repr(value)

    def read_value_ADC(self):
        """Read value from ADC and return dictionary"""

        out={}

        c=self.read(self.byte_mode)

        out['datetime']=datetime.datetime.now()
        if c==b'': return None
        data=c
        # print(data)
        channel=(data[0] & 0b00110000)>>4
        out['channel']=channel+1 #remember -  we a deside that channel of ADC start from 1

        value=(((data[0]&0b00001111)<<20)+(data[1]<<13)+(data[2]<<6)+(data[3]>>1) - 0x800000)
        value=value/self.config['channels'][channel+1]['gain']*self._koefficient
        out['value']=value

        if len(c)==5:
            out['timer']=data[4]
        return out

    def value_to_string(self,value):
        """Return string presentation of value reading from ADC"""

        if not value:
            return 'None'
        if 'timer' in value:
            return '%(datetime)s\tChannel %(channel)i\tValue %(value)i\tTimer %(timer)s'%value
        else:
            return '%(datetime)s\tChannel %(channel)i\tValue %(value)i'%value

    def print_value_ADC(self, value):
        """Just print value from ADC"""

        print(self.value_to_string(value))


    def read(self, length=1):
        """Read count byte from COM"""

        return self.serial.read(length)

    def close(self):
        """ Stop ADC and close COM port"""

        self.stop()
        self.serial.close()

#===============================================================================
# Intermal module function
#===============================================================================

    def _activate_channels(self):
        self.toADC(0x0, 0x0, 0x80+self.active_channels)

#===============================================================================
# Functions in according with documentation
#===============================================================================

    def set_active_channels(self, first=None, second=None, third=None, fourth=None):
        """Set active channels individualy. Avaiable values are True - channel active, False - channel disable,
        None - save original state"""
        self.stop()

        if first!=None:
            if (self.active_channels&0b0001)!=first:
                self.active_channels=self.active_channels^0b0001
        if second!=None:
            if (self.active_channels&0b0010)>>1!=second:
                self.active_channels=self.active_channels^0b0010
        if third!=None:
            if (self.active_channels&0b0100)>>2!=third:
                self.active_channels=self.active_channels^0b0100
        if fourth!=None:
            if (self.active_channels&0b1000)>>3!=fourth:
                self.active_channels=self.active_channels^0b1000
        self._activate_channels()

    def set_channel_input_type(self, channel, input_type):
        """"Set channel working mode.
         Avaiable values are for channel: 1...4;
         for type: 0-line A, 1-line B, 2-self voltage, 3-test mode"""

        ch={1:0b0001,2:0b0010,3:0b0100,4:0b1000}[channel]
        self.toADC(0x0, input_type, 0x90+ch)

    def set_channel_frequency(self, channel, frequency):
        """Set working frequency for the channel.
        Avaiable values are for channel: 1...4; for frequency: 5...1000"""

        c=2457600/(128*frequency)
        ch={1:0b0001,2:0b0010,3:0b0100,4:0b1000}[channel]
        sb=(int(c)&0xFF00)>>8
        mb=int(c)&0x00FF
        self.toADC((mb&0xF0)>>4, mb&0x0F, 0xB0+ch)

        self.toADC((sb&0xF0)>>4, sb&0x0F, 0xA0+ch)

    def set_gain_and_calibration(self, channel, gain=1, calibration=1):
        """Set for the channel gain value and calibration mode.
        Avaiable values for channel: 1...4; for gain: 1,2,4,8,16,32,64,128; for calibration: 0...7"""

        ch={1:0b0001, 2:0b0010, 3:0b0100, 4:0b1000}[channel]
        g={1:0b0, 2:0b1, 4:0b10, 8:0b11, 16:0b100, 32:0b101, 64:0b110, 128:0b111}[gain]
        self.toADC(calibration, g, 0xC0+ch)
        self.serial.flushOutput()

    def reinitialization(self, first=True, second=True, third=True, fourth=True):
        """Apply all changed parameters of ADC"""

        value=0
        if first:
            value+=0b0001
        if second:
            value+=0b0010
        if third:
            value+=0b0100
        if fourth:
            value+=0b1000
        self.toADC(0x0, 0x0, 0xD0+value)
        self._activate_channels()
        self.serial.flushOutput()


    def reset_timer(self):
        """Reset internal timer of ADC"""

        self.toADC(0x0, 0x0, 0xF0)

    def set_COM_speed(self, speed=19200):
        """Set the COM speed of the ADC. REMEMBER, that the next step should be set the same speed of the PC.
        Avaiable values are 2400, 4800, 9600, 19200, 38400, 57600 """

        sp={2400:0, 4800:1, 9600:2, 19200:3, 38400:4, 57600:5}[speed]
        self.toADC(0x5A, 0x5A, 0xE+sp)

    def set_address_EEPROM(self, address):
        """Set address pointer to next I/O operation. For reading address may be 0...127, for write 0..63"""

        self.toADC((address&0xf0)>>4,
                   address&0xf,
                   0xF2)

    def read_from_EEPROM(self, length):
        """Read 'length' bytes from EPPROM memmory of ADC. ADC will be stop, read data, restore working"""

        self.stop()

        values=[]
        for i in xrange(length):
            self.toADC2(0x0,0x0,0xF1)
            time.sleep(0.1)

            data=map(ord, self.read(2))
            if len(data)!=2:
                return None
            values.append(((data[1]&0x0F)<<4)+(data[0]&0x0F))

        self._activate_channels()
        return ''.join(map(chr, values))

    def record_byte_EEPROM(self, value):
        """Record byte value to EEPROM memory of ADC"""

        self.toADC((value&0xF0)>>4,
                    value&0xF,
                    0xF3)
        while ord(self.read())!=0xB0:
            time.sleep(0.5)

    def stop(self):
        """Send STOP command to ADC and clear COM stdout"""

        self.toADC(0x0, 0x0, 0xFF)
        self.serial.flushOutput()

    def read_params(self):
        """Return string with parameters in ADC. ADC will be stopped"""

        self.stop()
        self.toADC(0x0, 0x0, 0xF5)

        result=self.read(14)

        gains={0:1, 1:2, 2:4, 3:8, 4:16, 5:32, 6:64, 7:128}

        out=[]
        if len(result)!=14 or result[:2]!=b'\xee\xea':
            return 'Error while reading parameters: result = '+result
        result=result[2:]
        for channel,index in enumerate(range(0,12,3)):
            try:
                fs=((result[index])<<8)+(result[index+1])
                fs=2457600.0/(128*fs)
                ad7714=((result[index+2])&0b11000000)>>6
                calibration=((result[index+2])&0b00111000)>>3
                gain=((result[index+2])&0b111)
                gain=gains[gain]
                out.append('ADC_Channel #%i\tfrequency %i\tad7714_channel %i\tcalibration %i\tgain %i'%\
                           (channel+1, fs, ad7714,calibration, gain))
            except Exception:
                out.append('Error in ADC_channel %i : %s'%(channel+1, traceback.format_exc()))
        return '\n'.join(out)

    def set_byte_mode(self, mode=4):
        """ Switch 4 or 5 byte ADC output. Mode=4 for 4 bytes mode, mode=5 for 5 byte mode"""

        if self.byte_mode==mode:
            return

        if mode==5:
            self.toADC(0x0, 0x0, 0xF6)
            self.byte_mode=5
        else:
            self.toADC(0x0, 0x0, 0xF7)
            self.byte_mode=4

def human_bytes(list_of_bytes):
    """return Human readable string presentation of list bytes """

    if list_of_bytes=='': return
    out=[]
    out.append(repr(list_of_bytes))

    len_str_prefix=len(str(len(list_of_bytes)))

    out.append(' '*len_str_prefix+' |'+'|'.join(map(str, range(8)[::-1])))

    for i,value in enumerate(list_of_bytes):
        out.append('%s |%s'%(str(i).rjust(len_str_prefix),
                              '|'.join(bin(ord(value))[2:].rjust(8,'0'))))
    return '\n'.join(out)

def human_value_adc(list_of_bytes):
    """return Human readable string presentation of list bytes reading from ADC"""

    if list_of_bytes=='': return
    out=[]
    data=map(ord,list_of_bytes)
    out.append(datetime.datetime.now().strftime('%H:%M:%S.%f'))

    out.extend(human_bytes(list_of_bytes).splitlines())

    channel=(data[0] & 0b00110000)>>4
    out.append('channel #%s'%(channel+1))

    value=(((data[0]&0b00001111)<<20)+(data[1]<<13)+(data[2]<<6)+(data[3]>>1) - 0x800000)
    out.append('value %i'%value)

    if len(list_of_bytes)==5:
        timer=data[4]
        out.append('Timer %s'%timer)
    return '\n'.join(out)

if __name__=="__main__":
    core = PyE24lib({'port':'/dev/ttyUSB0',
                     'channels':{1:{'frequency':5,
                                    'input_type':0,
                                    'gain':1,
                                    'calibration':0},
                                 2:{'frequency':20,
                                    'input_type':1,
                                    'gain':2,
                                    'calibration':1},
                                 3:{'frequency':50,
                                    'input_type':3,
                                    'gain':32,
                                    'calibration':7},
                                 4:{'frequency':100,
                                    'input_type':2,
                                    'gain':128,
                                    'calibration':5},
                     }})
    try:
        print('version = '+__VERSION__)
        # core = PyE24lib({'port':'/dev/ttyUSB0',
        #                  'channels':{1:{'frequency':5,
        #                                 'input_type':0,
        #                                 'gain':1,
        #                                 'calibration':0},
        #                              2:{'frequency':20,
        #                                 'input_type':1,
        #                                 'gain':2,
        #                                 'calibration':1},
        #                              3:{'frequency':50,
        #                                 'input_type':3,
        #                                 'gain':32,
        #                                 'calibration':7},
        #                              4:{'frequency':100,
        #                                 'input_type':2,
        #                                 'gain':128,
        #                                 'calibration':5},
        #                  }})



        parameters=core.read_params()

        if parameters!='ADC_Channel #1\tfrequency 5\tad7714_channel 0\tcalibration 0\tgain 1\nADC_Channel #2\tfrequency 20\tad7714_channel 1\tcalibration 1\tgain 2\nADC_Channel #3\tfrequency 50\tad7714_channel 3\tcalibration 7\tgain 32\nADC_Channel #4\tfrequency 100\tad7714_channel 2\tcalibration 5\tgain 128':
            raise Exception('self test failed, parameters:\n'+parameters)
        else:
            print('Self-test done successfully')
        # core.close()


    except Exception:
        traceback.print_exc()
    finally:
        core.close()
