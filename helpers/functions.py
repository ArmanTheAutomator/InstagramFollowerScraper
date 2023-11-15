import datetime
from helpers.user import generate_user_info
import random
import os
from os import listdir
from os.path import isfile, join
import time
from helpers.files import read_txt

def get_acc_info():
    users = read_txt('names.txt')
    data = []
    for user in users:
        user = generate_user_info(user)
        images = [f for f in listdir('images') if isfile(join('images', f))]
        index = random.randint(0,len(images)-1)
        image = os.path.abspath(os.getcwd()) + '\images\\' + images[index]
        user['img'] = image
        data.append(user)
    return data
    
def formatted_time(t, hours = False):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    if hours:
        return '{:d}:{:02d}:{:02d}'.format(h, m, s)
    else: 
        return '{:02d}:{:02d}'.format(m, s)

def countdown(t, message='Waiting'):
    while t:
        mins, secs = divmod(t, 60) 
        hours, mins = divmod(mins, 60)
        timer = '{:02d}:{:02d}:{:02d}'.format(hours, mins, secs) 
        print(f'\r{message}: {timer}                    ', end="") 
        time.sleep(1) 
        t -= 1
    print('\rWaiting is over                                          ')
    
def data_countdown(message='More Data Collected', time_gap=None):
    print(f'\r{message}', end="")
    
    if time_gap:
        time.sleep(time_gap)

def execution_time(start_time, data_length=None):
    print('\nExecution Completed\nReport:\n================================')  
    print('Execution time:', datetime.timedelta(seconds= int(time.time() - start_time)))

    if data_length:
        print(f'Total {data_length} Data Collected/ Inserted Into File')