import os
from datetime import datetime as dt

def mk_dir_of_day():
    try:
       # os.mkdir(os.path.join(os.getcwd(), 'data/{:%F}'.format(dt.utcnow())))
        os.mkdir('/mnt/data_collector/data/{:%F}'.format(dt.utcnow()))
    except FileExistsError as e:
        pass

def mk_file_of_hour(data):
    #with open(os.path.join(os.getcwd(), 'data/{:%F/%H}.txt'.format(dt.utcnow())), 'a') as file:
    #with open('/mnt/data_collector/{:%F/%H}.txt'.format(dt.utcnow())) as file:
    with open('/mnt/data_collector/data/{:%F/%H}.txt'.format(dt.utcnow()), 'a') as file:
        file.write(data)


if __name__ == '__main__':
    mk_dir_of_day()
