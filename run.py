import tornado.ioloop
import tornado.web
import tornado.websocket
import uuid


clients = {} # uid: Client
rooms   = {} # bid: Room
uids    = {} # self: uid


class Client():
    def __init__(self, uid, socket):
        self.uid = uid
        self.socket = socket
        self.board = []
        self.rival = None
        self.room = None


class Room():
    def __init__(self, bid, name):
        self.bid = bid # black uuid
        self.wid = None # white uuid
        self.board = []
        self.bsocket = None
        self.wsocket = None
        self.name = name
        self.num = 1
    
    def info(self):
        return {'name': self.name, 'white': self.wid, 'num': self.num}
    
    def get_board(self, uid):
        if uid == self.bid or uid == self.wid:
            return self.board
        return False
    
    def lose(self, uid):
        if uid == self.bid:
            self.wsocket.write_message('white win!')
        elif uid == self.wid:
            self.bsocket.write_message('black win!')


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class RoomHandler(tornado.web.RequestHandler):
    def get(self):
        d = {}
        for r in rooms:
            d[r] = rooms[r].info()
        self.write(d)


class CreateRoom(tornado.web.RequestHandler):
    def get(self):
        name = self.get_argument('name', 'placeholder')
        uid = self.get_argument('uuid')
        rooms[uid] = Room(uid, name)
        rooms[uid].bsocket = clients[uid].socket
        clients[uid].room = rooms[uid]
        self.write(rooms[uid].info())


class JoinRoom(tornado.web.RequestHandler):
    def get(self):
        bid = self.get_argument('bid')
        uid = self.get_argument('uuid')
        room = rooms[bid]
        room.wid = uid
        room.num = 2
        room.wsocket = clients[uid].socket
        room.board = []
        clients[uid].rival = clients[bid]
        clients[uid].room = room
        clients[uid].board = room.board
        clients[bid].rival = clients[uid]
        clients[bid].board = room.board
        clients[bid].room = room
        clients[uid].socket.write_message('start')
        clients[bid].socket.write_message('start')
        self.write('join')


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        if self not in clients:
            uid = str(uuid.uuid4())
            c = Client(uid, self)
            clients[uid] = c
            uids[self] = uid
            self.write_message('uid ' + uid)
            print("WebSocket opened")

    def on_message(self, message):
        print('Message:', message)
        color, x, y = message.split(',')
        board = self.get_board()
        if 0 < int(x) < 20 and 0 < int(y) < 20 and (x, y) not in board:
            u = uids[self]
            c = clients[u]
            c.rival.socket.write_message(message)
            self.write_message(message)
            if self.check_win(int(x), int(y)):
                print(color, 'win')
                c.rival.socket.write_message(color + ' win!')
                self.write_message(color + ' win!')

    def on_close(self):  # remove from clients, delete room, board, win condition
        print("WebSocket closed")
        uid = uids[self]
        c = clients[uid]
        if c.rival:
            c.room.lose(uid)
            del rooms[c.room.bid]
        del clients[uid]



    def check_win(self, x, y):
        board = self.get_board()
        board.append((x, y))
        moves = board[(len(board)-1) % 2::2]
        for i in range(0, 5):  # horizontal
            for j in range(0, 5):
                if (x-i+j, y) not in moves:
                    break
                elif j == 4:
                    return True
        for i in range(0, 5):  # vertical
            for j in range(0, 5):
                if (x, y-i+j) not in moves:
                    break
                elif j == 4:
                    return True
        for i in range(0, 5):
            for j in range(0, 5):
                if (x-i+j, y+i-j) not in moves:
                    break
                elif j == 4:
                    return True
        for i in range(0, 5):
            for j in range(0, 5):
                if (x-i+j, y-i+j) not in moves:
                    break
                elif j == 4:
                    return True
        return False

    def get_board(self):
        uid = uids[self]
        return clients[uid].board


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/ws', EchoWebSocket),
        (r'/room', RoomHandler),
        (r'/create', CreateRoom),
        (r'/join', JoinRoom),
    ], debug=True, autoreload=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()
