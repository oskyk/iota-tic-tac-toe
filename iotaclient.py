from iota import Iota
from iota.crypto.addresses import AddressGenerator
from iota.transaction import ProposedTransaction
from iota.types import TryteString
import json
from random import randint
from configparser import ConfigParser
import os


class IotaClient(object):
    def __init__(self):
        conf = ConfigParser()
        path = os.path.join(os.path.dirname(__file__), 'config/config.txt')
        conf.read(path)
        self.iota = Iota(conf.get('IOTA', 'node'), conf.get('IOTA', 'seed'))
        self.generator = AddressGenerator(self.iota.seed)
        self.match_making_addr = self.generator.get_addresses(1)

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

    def get_match(self):
        matches = self.get_msgs(1, msg_type='matches')
        matches_open = [match['id'] for match in list(filter(lambda match: not match['closing'], matches))]
        matches_close = [match['id'] for match in list(filter(lambda match: match['closing'], matches))]
        for match in matches_close:
            if match in matches_open:
                matches_open.remove(match)
        if len(matches_open) >= 1:
            self.send_msg(self.generator.get_addresses(1)[0], {'type': 'matches', 'closing': True, 'id': matches_open[0]})
            return matches_open[0], 1
        else:
            match_id = randint(100, 1e9)
            self.send_msg(self.generator.get_addresses(1)[0], {'type': 'matches', 'closing': False, 'id': match_id})
            return match_id, 0
