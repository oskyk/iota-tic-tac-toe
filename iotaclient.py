from iota import Iota
from iota.crypto.addresses import AddressGenerator
from iota.transaction import ProposedTransaction
from iota.types import TryteString
import json
from random import randint
from configparser import ConfigParser
import os
from pymemcache.client import base


class IotaClient(object):
    def __init__(self):
        conf = ConfigParser()
        path = os.path.join(os.path.dirname(__file__), 'config/config.txt')
        conf.read(path)
        self.iota = Iota(conf.get('IOTA', 'node'), conf.get('IOTA', 'seed'))
        self.generator = AddressGenerator(self.iota.seed)
        self.match_making_addr = self.generator.get_addresses(1)
        self.memcached = base.Client(('127.0.0.1', 11211))

    def send_msg(self, addr, msg):
        pt = [ProposedTransaction(addr, 0, message=TryteString.from_string(json.dumps(msg)))]
        return self.iota.send_transfer(depth=1, transfers=pt)['bundle'].transactions[0].hash

    def get_msgs(self, addr_index, msg_type):
        account_data = self.iota.get_account_data(int(addr_index))
        msgs = []
        for bundle in account_data['bundles']:
            msgs.append(json.loads(bundle.get_messages()[0]))
            msgs[-1]['tx_hash'] = str(bundle.transactions[0].hash)
        return list(filter(lambda msg: msg['type'] == msg_type, msgs))

    def save_move(self, addr_index, player, x, y):
        addr = self.generator.get_addresses(int(addr_index))[0]
        return self.send_msg(addr, {'type': 'move', 'player': player, 'x': x, 'y': y})

    def get_moves(self, addr_index):
        return self.get_msgs(addr_index, msg_type='move')

    def open_match(self):
        match_id = randint(100, 1e9)
        self.memcached.set('open', str(match_id))
        return match_id

    def get_open_match(self):
        try:
            return int(self.memcached.get('open'))
        except TypeError:
            return None

    def close_match(self):
        self.memcached.delete('open')

    def get_match(self):
        match_open = self.get_open_match()
        if match_open:
            self.close_match()
            return match_open, 1
        else:
            return self.open_match(), 0
