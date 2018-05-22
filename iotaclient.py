from iota import Iota
from iota.crypto.addresses import AddressGenerator
from iota.transaction import ProposedTransaction
from iota.types import TryteString
import json
from random import randint
from configparser import ConfigParser
import os
from pymemcache.client import base
import pickle


class IotaClient(object):
    def __init__(self):
        conf = ConfigParser()
        path = os.path.join(os.path.dirname(__file__), 'config/config.txt')
        conf.read(path)
        self.iota = Iota(conf.get('IOTA', 'node'), conf.get('IOTA', 'seed'))
        self.generator = AddressGenerator(self.iota.seed)
        self.match_making_addr = self.generator.get_addresses(1)
        self.memcached = base.Client(('127.0.0.1', 11211))

    def get_addr(self, addr_index):
        try:
            addr = pickle.loads(self.memcached.get(str(addr_index) + 'addr'))
        except TypeError:
            addr = self.generator.get_addresses(int(addr_index))[0]
            self.memcached.set(str(addr_index) + 'addr', pickle.dumps(addr))
        return addr

    def send_msg(self, addr_index, msg):
        addr = self.get_addr(addr_index)
        pt = [ProposedTransaction(addr, 0, message=TryteString.from_string(json.dumps(msg)))]
        msg_hash = str(self.iota.send_transfer(depth=1, transfers=pt)['bundle'].transactions[0].hash)
        self.add_cached_msg(addr_index, msg, msg_hash)
        return msg_hash

    def get_msgs(self, addr_index, msg_type=None):
        msgs = self.memcached.get(str(addr_index))
        try:
            msgs = json.loads(msgs.decode())
        except (AttributeError, TypeError):
            msgs = self.get_iota_msgs(addr_index)
            self.memcached.set(str(addr_index), json.dumps(msgs), expire=300)
        if msg_type is not None:
            msgs = list(filter(lambda msg: msg['type'] == msg_type, msgs))
        return msgs

    def get_iota_msgs(self, addr_index):
        account_data = self.iota.get_account_data(int(addr_index))
        msgs = []
        for bundle in account_data['bundles']:
            msgs.append(json.loads(bundle.get_messages()[0]))
            msgs[-1]['tx_hash'] = str(bundle.transactions[0].hash)
        return msgs

    def add_cached_msg(self, addr_index, msg, msg_hash):
        msgs = self.get_msgs(addr_index)
        msgs.append(msg)
        msgs[-1]['tx_hash'] = msg_hash
        self.memcached.set(str(addr_index), json.dumps(msgs), expire=300)

    def save_move(self, addr_index, player, x, y):
        return self.send_msg(addr_index, {'type': 'move', 'player': player, 'x': x, 'y': y})

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
