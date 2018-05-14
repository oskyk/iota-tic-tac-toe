from iota import Iota
from iota.crypto.addresses import AddressGenerator
from iota.transaction import ProposedTransaction
from iota.types import TryteString
import json

IOTA_NODE = 'http://node.deviceproof.org:14265'
IOTA_SEED = 'CTRRJZYQCNIWIGVBYEAUBQWXWHHCAUFNVKFEG9BKRCYWLKIV9CEDUWVIYADCFPHMWYDWDSVCKBQLJGKHV'


class IotaClient(object):
    def __init__(self):
        self.iota = Iota(IOTA_NODE, IOTA_SEED)
        self.generator = AddressGenerator(self.iota.seed)
        self.match_making_addr = self.generator.get_addresses(1)

    def send_msg(self, addr, msg):
        pt = [ProposedTransaction(addr, 0, message=TryteString.from_string(json.dumps(msg)))]
        print(self.iota.send_transfer(depth=1, transfers=pt))

    def get_msgs(self, addr_index, msg_type):
        account_data = self.iota.get_account_data(int(addr_index))
        msgs = []
        for bundle in account_data['bundles']:
            msgs.append(json.loads(bundle.get_messages()[0]))
        return list(filter(lambda msg: msg['type'] == msg_type, msgs))

    def save_move(self, addr_index, player, x, y):
        addr = self.generator.get_addresses(int(addr_index))[0]
        self.send_msg(addr, {'type': 'move', 'player': player, 'x': x, 'y': y})

    def get_moves(self, addr_index):
        return self.get_msgs(addr_index, msg_type='move')
