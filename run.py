from app import *

if __name__ == '__main__':
    E24 = PyE24lib(parameters)
    while True:
        mk_dir_of_day()
        while True:
            try:
                mk_file_of_hour(read_value_from_ttyUSB(E24) + '\n')
            except FileNotFoundError as ex:
                break
