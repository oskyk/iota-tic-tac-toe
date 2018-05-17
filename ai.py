from collections import Counter
from random import randint
from datetime import datetime


class GameOver(Exception):
    pass


class MoveNotFound(Exception):
    pass


class TttAI(object):
    def __init__(self, iota_client, addr_index):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.turn = 0
        self.iota_client = iota_client
        self.addr_index = addr_index
        self.iota_client.close_match(addr_index)
        self.play()

    def check_row(self, iter, enemy, friend):
        for x, row in enumerate(iter):
            count = Counter(row)
            if count[enemy] == 3 or count[friend] == 3:
                raise GameOver()
            if count[enemy] == 2 and count[friend] == 0:
                return x
        return False

    def check_diag(self, enemy, friend):
        rows = [[], []]
        for i in range(0, 3):
            rows[0].append(self.board[i][i])
            rows[1].append(self.board[i][-i-1])
        return self.check_row(rows, enemy, friend)

    def check_board(self, enemy='x', friend='o'):
        return {
            'row': self.check_row(self.board, enemy, friend),
            'column': self.check_row(zip(*self.board), enemy, friend),
            'diag': self.check_diag(enemy, friend)
        }

    def available_move(self, move):
        return not (len(set(move)) == 1 and set(move).pop() is False)

    def get_move_point(self, in_x, move_type):
        if move_type == 'row':
            return in_x, next(x for x, item in enumerate(self.board[in_x]) if item == 0)
        elif move_type == 'column':
            return next(y for y, item in enumerate(list(zip(*self.board))[in_x]) if item == 0), in_x
        elif move_type == 'diag':
            for i in range(0, 3):
                if in_x == 0:
                    if self.board[i][i] == 0:
                        return i, i
                else:
                    if self.board[i][2-i] == 0:
                        return i, 2 - i
        else:
            raise ValueError('Invalid move type')

    def test_move(self, enemy, friend):
        move = self.check_board(enemy, friend)
        if self.available_move(move):
            move_type = next((item for item in move if move[item] is not False), False)
            if move_type:
                return self.get_move_point(move[move_type], move_type)
        return None, None

    def get_move(self):
        x, y = self.test_move('o', 'x')
        if x is not None:
            return x, y
        x, y = self.test_move('x', 'o')
        if x is not None:
            return x, y
        raise MoveNotFound()

    def random_move(self):
        while True:
            x = randint(0, 2)
            y = randint(0, 2)
            if self.board[x][y] == 0:
                return x, y

    def get_point(self):
        try:
            return self.get_move()
        except MoveNotFound:
            return self.random_move()

    def fetch_opponent(self):
        move = False
        start_time = datetime.now()
        while not move:
            try:
                move = self.iota_client.get_moves(self.addr_index)[self.turn]
            except IndexError:
                pass
            if (datetime.now() - start_time).total_seconds() > 1800 and not move:
                raise GameOver('Timeout')
        print('Found move', move)
        self.board[int(move['x'])][int(move['y'])] = 'x'
        self.turn += 1

    def my_turn(self):
        x, y = self.get_point()
        self.board[x][y] = 'o'
        self.turn += 1
        self.iota_client.save_move(self.addr_index, 'o', str(x), str(y))

    def play(self):
        try:
            while True:
                if self.turn == 9:
                    raise GameOver()
                elif self.turn % 2 == 0:
                    self.fetch_opponent()
                else:
                    self.my_turn()
        except GameOver:
            return
