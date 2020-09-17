import os
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

while True:
    os.system('python requestdata.py')

    print('sleep 30 seconds')
    time.sleep(30)