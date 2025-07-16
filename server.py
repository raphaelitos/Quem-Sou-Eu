import socket
from game import Game
from protocol import MSG_TYPE, pack

HOST = '0.0.0.0'
PORT = 5000

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(2)
        conn1, _ = s.accept()
        conn2, _ = s.accept()
        game = Game(conn1, conn2)
        game.setup()
        game.send(1, MSG_TYPE['TURN'], None)
        game.loop()
        conn1.close()
        conn2.close()

if __name__ == '__main__':
    main()
