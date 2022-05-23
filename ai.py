import random


NILSCORE = 7
X1SCORE = 15
X2SCORE = 400
X3SCORE = 1800
X4SCORE = 100000
O1SCORE = 35
O2SCORE = 800
O3SCORE = 15000
O4SCORE = 800000
# rival: X, self: O


class Bot():
    def __init__(self):
        self.moves = []
        self.score_table = []  # [i][j]: {total, d0, d45, d90, d135}
        self.board = []  # b, w, 0, -1
        self.color = 'white'  # default
        self.init()

    def init(self):
        for x in range(15):
            row = []
            row2 = []
            for y in range(15):
                row.append(
                    {'total': 0, 'd0': 0, 'd45': 0, 'd90': 0, 'd135': 0})
                row2.append(0)
            self.score_table.append(row)
            self.board.append(row2)

    def move(self, x, y, color):  # int x, int y
        self.board[y-1][x-1] = color
        self.moves.append((x, y))
        self.update_score_table()

    def test(self, x, y):
        for i in range(1, 16):
            for j in range(1, 16):
                if (i, j) not in self.moves:
                    self.moves.append((i, j))
                    return i, j

    def update_score_table(self):
        lastmove = self.moves[-1]
        x, y = lastmove[0], lastmove[1]
        for i in range(-4, 5):
            self.update_score(x, y, +i, +i)
            self.update_score(x, y, +i, 0)
            self.update_score(x, y, +i, -i)
            self.update_score(x, y, 0, i)

    def update_score(self, x, y, i, j):
        if x+i < 1 or x+i > 15 or y+j < 1 or y+j > 15:
            return
        square = self.score_table[y+j-1][x+i-1]
        if self.board[y+j-1][x+i-1] != 0:
            square['total'] = 0
            return

        if i*j > 0:
            l = [self.move2board(x+i+k, y+j+k) for k in range(-4, 5)]
            square['d135'] = self.calculate(l)
            # print(x+i, y+j, l, self.calculate(l))
        elif j == 0:
            l = [self.move2board(x+i+k, y) for k in range(-4, 5)]
            square['d0'] = self.calculate(l)
            # print(x+i, y+j, l, self.calculate(l))

        elif i == 0:
            l = [self.move2board(x, y+j+k) for k in range(-4, 5)]
            square['d90'] = self.calculate(l)
            # print(x+i, y+j, l, self.calculate(l))
        else:
            l = [self.move2board(x+i+k, y+j-k) for k in range(-4, 5)]
            square['d45'] = self.calculate(l)
            # print(x+i, y+j, l, self.calculate(l))

        square['total'] = square['d0'] + \
            square['d45'] + square['d90'] + square['d135']
        # print('update', (x+i, y+j), square)

    def calculate(self, l):
        result = 0
        # b w w w 0 0 0 0 0
        for i in range(5):
            color = 0
            num = 0
            for j in range(5):
                if l[i+j] == 0:
                    continue
                elif l[i+j] == -1:
                    num = 0
                    break
                if l[i+j] != color:
                    if color == 0:
                        color = l[i+j]
                        num = num + 1
                    else:
                        num = 0
                        break
                else:
                    num = num + 1
            result = result + self.score(color, num)
        return result

    def score(self, color, num):
        if num == 0:
            return 0
        elif num == 1:
            return 15 if color == 'b' else 35
        elif num == 2:
            return 400 if color == 'b' else 800
        elif num == 3:
            return 1800 if color == 'b' else 15000
        elif num == 4:
            return 100000 if color == 'b' else 800000

    def move2board(self, x, y):
        if 0 <= x-1 < 15 and 0 <= y-1 < 15:
            return self.board[y-1][x-1]
        return -1  # out of board

    def get_score(self, x, y):
        return self.score_table[y-1][x-1]

    def next_move(self):
        m = 0
        l = []
        for i in range(15):
            for j in range(15):
                if self.score_table[i][j]['total'] > m:
                    m = self.score_table[i][j]['total']
                    l[:] = []
                    l.append((j+1, i+1))
                elif self.score_table[i][j]['total'] == m:
                    l.append((j+1, i+1))
        return random.choice(l)


if __name__ == '__main__':
    bot = Bot()
    bot.move(8, 8, 'b')
    bot.move(9, 8, 'w')
    bot.move(8, 9, 'b')
    # print(bot.get_score(14, 14))
    # l = [0, 0, 0, 0, 0, 'w', -1, -1, -1]
    # print(bot.calculate(l))
