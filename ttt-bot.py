from iotaclient import IotaClient
from ai import TttAI
from time import sleep
from threading import Thread


iota_client = IotaClient()
prev_matches = set()

while True:
    try:
        matches = set(iota_client.get_open_matches())
        intersection = matches.intersection(prev_matches)
        for match in intersection:
            thread = Thread(target=TttAI, kwargs={'iota_client': iota_client, 'addr_index': int(match)})
            thread.start()
            print('Match id: {} started!'.format(match))
        prev_matches = matches
    except Exception as error:
        print(str(error))
    sleep(20)
