import datetime
import json
from django.core.management import BaseCommand
from django.db.models import DurationField, ExpressionWrapper, F, IntegerField, Sum
from django.utils import timezone

from config.settings import BASE_DIR, STATICFILES_DIRS
from worktimeprivate.models import CustomUser, Employee, Employer, Timesheet, WorkTime
import calendar
import asyncio
from asyncio import Lock, Event
from bleak import BleakClient, BleakScanner
# https://bleak.readthedocs.io/en/latest/api/scanner.html

# address = "24:71:89:cc:09:05"
# MODEL_NBR_UUID = "2A24"
# # def change_string_smwhere():
lst = []
async def main():
    lock = Lock()
    stop_event = Event()
    
    '''Устанавливаем задачу - распечатываем данные устройств'''
    def callback(device, advertising_data):
        if (device) not in [i[0] for i in lst]:
            # print('device', device, 'advertising_data',  advertising_data)
            lst.append((device, advertising_data))
            print('lst', lst)#lst [(BLEDevice(A8:34:6A:11:45:3D, Galaxy A30), AdvertisementData(local_name='Galaxy A30', service_data={'0000fef3-0000-1000-8000-00805f9b34fb': b'J\x17#JIHS\x112.\xa6\xd5\x88b\xeb\xab\xd5T\xb8Am\xd1&\xcc#q\xcd'}, service_uuids=['00001105-0000-1000-8000-00805f9b34fb', '0000110a-0000-1000-8000-00805f9b34fb', '0000110c-0000-1000-8000-00805f9b34fb', '0000110e-0000-1000-8000-00805f9b34fb', '00001112-0000-1000-8000-00805f9b34fb', '00001115-0000-1000-8000-00805f9b34fb', '00001116-0000-1000-8000-00805f9b34fb', '0000111f-0000-1000-8000-00805f9b34fb', '0000112d-0000-1000-8000-00805f9b34fb', '0000112f-0000-1000-8000-00805f9b34fb', '00001132-0000-1000-8000-00805f9b34fb', '00001200-0000-1000-8000-00805f9b34fb', '00001800-0000-1000-8000-00805f9b34fb', '00001801-0000-1000-8000-00805f9b34fb', 'a82efa21-ae5c-3dde-9bbc-f16da7b16c5a'], rssi=-66))]
        
        else:
            print('Finish')
            stop_event.set()
        #     print('lst=================', lst)
        #     scanner.stop()
        #     return lst
    async with BleakScanner(callback) as scanner:
        
        
        # Important! Wait for an event to trigger stop, otherwise scanner
        # will stop immediately.
        await stop_event.wait()

    # scanner stops when block exits    
    async with BleakScanner() as client:
        async with lock:
            model_numbers = await client.discover()
            
    #         for d in model_numbers:
    #             print('model_number',d)
    #             return d
        
        # print("Model Number: {0}".format("".join(map(chr, model_number))))
    # async def main(address):
    # async with BleakClient(address) as client:
    #     model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        # model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        # print("Model Number: {0}".format("".join(map(chr, model_number))))

    # num_days = [(2025, 1, [(1, 1, 'Tuesday'), (2, 0, 'Monday'), (3, 6, 'Sunday'), (4, 5, 'Saturday'), (5, 4, 'Friday'), (6, 3, 'Thursday'), (7, 2, 'Wednesday'), (8, 1, 'Tuesday'), (9, 0, 'Monday'), (10, 6, 'Sunday'), (11, 5, 'Saturday'), (12, 4, 'Friday'), (13, 3, 'Thursday'), (14, 2, 'Wednesday'), (15, 1, 'Tuesday'), (16, 0, 'Monday'), (17, 6, 'Sunday'), (18, 5, 'Saturday'), (19, 4, 'Friday'), (20, 3, 'Thursday'), (21, 2, 'Wednesday'), (22, 1, 'Tuesday'), (23, 0, 'Monday'), (24, 6, 'Sunday'), (25, 5, 'Saturday'), (26, 4, 'Friday'), (27, 3, 'Thursday'), (28, 2, 'Wednesday'), (29, 1, 'Tuesday'), (30, 0, 'Monday'), (31, 6, 'Sunday')]), (2025, 2, [(1, 5, 'Saturday'), (2, 4, 'Friday'), (3, 3, 'Thursday'), (4, 2, 'Wednesday'), (5, 1, 'Tuesday'), (6, 0, 'Monday'), (7, 6, 'Sunday'), (8, 5, 'Saturday'), (9, 4, 'Friday'), (10, 3, 'Thursday'), (11, 2, 'Wednesday'), (12, 1, 'Tuesday'), (13, 0, 'Monday'), (14, 6, 'Sunday'), (15, 5, 'Saturday'), (16, 4, 'Friday'), (17, 3, 'Thursday'), (18, 2, 'Wednesday'), (19, 1, 'Tuesday'), (20, 0, 'Monday'), (21, 6, 'Sunday'), (22, 5, 'Saturday'), (23, 4, 'Friday'), (24, 3, 'Thursday'), (25, 2, 'Wednesday'), (26, 1, 'Tuesday'), (27, 0, 'Monday'), (28, 6, 'Sunday')]), (2025, 3, [(1, 2, 'Wednesday'), (2, 1, 'Tuesday'), (3, 0, 'Monday'), (4, 6, 'Sunday'), (5, 5, 'Saturday'), (6, 4, 'Friday'), (7, 3, 'Thursday'), (8, 2, 'Wednesday'), (9, 1, 'Tuesday'), (10, 0, 'Monday'), (11, 6, 'Sunday')])]
    # print(num_days[0][2])
    # str_to_insert = 'smth\n'
    # data_insert = list(str_to_insert)
    # data_write = []
    # with open('worktimeprivate/templates/worktimeprivate/d.html', 'r') as f:
    #   data_read = f.readlines()
    #   data_write = data_read[0:3]+data_insert+data_read[3:]
    #   with open('worktimeprivate/templates/worktimeprivate/d.html', 'w') as ff:
    #     print(data_read[3:])
    #     ff.writelines(data_write)
         
    
# import requests
# def list_nat_holidays(cntry_code, year):#На входе буквы страны, список годов
#       # url = 'https://api.first.org/data/v1/countries'
#     #   total_lst = [i for i in year]
#       total_lst_year = []
#       for i in year:
#         url = f'https://date.nager.at/api/v3/publicholidays/{i}/{cntry_code}'
#         #   'https://api.api-ninjas.com/v1/holidays?country={cntry_code}&year={year}&type=public_holiday'
#         r = requests.get(url)
#         total_lst_year=total_lst_year[:]+r.json()
    
      
class Command(BaseCommand):
   
    def handle(self, *args, **options):
    
    #   change_string_smwhere()
    #   asyncio.run(main(address))
        asyncio.run(main())
      
      # list_nat_holidays('rU', [2022,2023,2024])