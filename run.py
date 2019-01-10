import tornado.ioloop
import tornado.web
import tornado.websocket
import uuid


clients = []
board = []

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class EchoWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        if self not in clients:
            clients.append(self)

    def on_message(self, message):
        print('Message:', message)
        color, x, y = message.split(',')
        if 0 < int(x) < 20 and 0 < int(y) < 20 and (x, y) not in board:
            for c in clients:
                c.write_message(message)
            if self.check_win(int(x), int(y)):
                print(color, 'win')
                for c in clients:
                    c.write_message('win')

    def on_close(self):
        print("WebSocket closed")
        clients.remove(self)
        board.clear()

    def check_win(self, x, y):
        board.append((x, y))
        moves = board[ (len(board)-1) % 2 ::2]
        for i in range(0, 5): # horizontal
            for j in range(0, 5):
                if (x-i+j, y) not in moves:
                    break
                elif j == 4:
                    return True
        for i in range(0, 5): # vertical
            for j in range(0, 5):
                if (x, y-i+j) not in moves:
                    break
                elif j == 4:
                    return True
        for i in range(0, 5):
            for j in range(0, 5):
                if (x-i+j, y+i-j) not in moves:
                    break
                elif  j == 4:
                    return True
        for i in range(0, 5):
            for j in range(0, 5):
                if (x-i+j, y-i+j) not in moves:
                    break
                elif  j == 4:
                    return True
        return False
                    


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/ws', EchoWebSocket),
    ], debug=True, autoreload=True)


if __name__ == '__main__':
    app = make_app()
    app.listen(8000)
    tornado.ioloop.IOLoop.current().start()