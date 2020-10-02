import os
import time
import logging

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(format='[%(asctime)s.%(msecs)03d] - %(levelname)s: %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

wait = 30

while True:
    os.system('python requestdata.py')

    logging.info('sleep %s seconds', wait)
    time.sleep(wait)