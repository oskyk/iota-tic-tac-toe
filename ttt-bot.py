from iotaclient import IotaClient
from ai import TttAI
from time import sleep
from threading import Thread


iota_client = IotaClient()
prev_match = 0

while True:
    try:
        match = iota_client.get_open_match()
        if match and match == prev_match:
            thread = Thread(target=TttAI, kwargs={'iota_client': iota_client, 'addr_index': int(match)})
            thread.start()
            print('Match id: {} started!'.format(match))
        prev_match = match
    except Exception as error:
        print(str(error))
    sleep(10)
