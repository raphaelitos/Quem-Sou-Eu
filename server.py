import socket
import threading
import random
import string
from protocol import *
from game import Game

HOST = '0.0.0.0'
PORT = 5000

# === framing por linha ===
_buffers = {}  # conn -> bytes

def recv_line(conn):
    buf = _buffers.get(conn, b'')
    while b'\n' not in buf:
        chunk = conn.recv(1024)
        if not chunk:
            return None
        buf += chunk
    line, sep, rest = buf.partition(b'\n')
    _buffers[conn] = rest
    return line + sep

# === gerenciamento de salas ===
rooms = {}             # code -> Room
rooms_lock = threading.Lock()

class Room:
    def __init__(self, code, creator_conn):
        self.code = code
        self.creator = creator_conn
        self.joiner = None
        self.ready = threading.Event()

def generate_code(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def handle_client(conn, addr):
    try:
        raw = recv_line(conn)
        if raw is None:
            conn.close()
            return
        t, content = unpack(raw)

        if t == MSG_TYPE['CREATE_ROOM']:
            code = generate_code()
            room = Room(code, conn)
            with rooms_lock:
                rooms[code] = room
            conn.send(pack(MSG_TYPE['ROOM_CREATED'], code))
            print(f"[Lobby] Sala {code} criada por {addr}, aguardando par...")
            room.ready.wait()
            start_game(room.creator, room.joiner)
            with rooms_lock:
                del rooms[code]

        elif t == MSG_TYPE['JOIN_ROOM']:
            code = content
            with rooms_lock:
                room = rooms.get(code)
            if not room:
                conn.send(pack(MSG_TYPE['ERROR'], 'Sala não encontrada.'))
                conn.close()
                return
            room.joiner = conn
            room.ready.set()
            conn.send(pack(MSG_TYPE['ROOM_JOINED'], code))
            room.creator.send(pack(MSG_TYPE['ROOM_JOINED'], code))
            print(f"[Lobby] Cliente {addr} entrou na sala {code}.")

        else:
            conn.send(pack(MSG_TYPE['ERROR'], 'Comando inválido no lobby.'))
            conn.close()

    except Exception as e:
        print(f"[Erro no lobby] {e}")
        conn.close()

def start_game(conn1, conn2):
    try:
        game = Game(conn1, conn2)
        game.setup()
        game.send(1, MSG_TYPE['TURN'], None)
        game.loop()
    except Exception as e:
        print(f"[Erro no jogo] {e}")
    finally:
        conn1.close()
        conn2.close()
        print("[Jogo] Partida encerrada, conexões fechadas.")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        print(f"[Servidor] À escuta em {HOST}:{PORT}")
        while True:
            conn, addr = sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == '__main__':
    main()
