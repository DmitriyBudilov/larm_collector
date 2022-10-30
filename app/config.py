parameters={'port': '/dev/ttyUSB0',            # COM port which attached device
            'five_byte_mode': True,            # Enable internal timer
            'channels': {                      # Internal dictionary which describes channels parameters
                         #1: {                  # Enable channel 1
                         #    'frequency':  50,  # Set frequency to 100Hz
                         #    'input_type': 0,  # Set channel input to Line A
                         #    'gain': 1,        # Set Gain level to one
                         #    'calibration': 6  # Disable any calibration
                         #    },
                         #2: {                  # Enable channel 1
                         #    'frequency':  50,   # Set frequency to 100Hz
                         #    'input_type': 0,  # Set channel input to Line A
                         #    'gain': 1,        # Set Gain level to one
                         #    'calibration': 6  # Disable any calibration
                         #    },
                         3: {                  # Enable channel 1
                             'frequency':  50,  # Set frequency to 100Hz
                             'input_type': 0,  # Set channel input to Line A
                             'gain': 1,        # Set Gain level to one
                             'calibration': 6  # Disable any calibration
                         #    },
                         #4: {                  # Enable channel 1
                         #    'frequency':  50,  # Set frequency to 100Hz
                         #    'input_type': 0,  # Set channel input to Line A
                         #    'gain': 1,        # Set Gain level to one
                         #    'calibration': 6  # Disable any calibration
                             }
                        }
            }
