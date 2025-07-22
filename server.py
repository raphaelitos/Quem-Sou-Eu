import socket
import threading
import random
import string
from protocol import *
from game import Game

HOST = '0.0.0.0'
PORT = 5000

# (conn -> bytes pendentes)
_buffers = {}

def recv_line(conn):
    """
    Lê até o '\n' de uma conexão, mantém o restante no buffer.
    Retorna a linha completa (com '\n') ou None se desconectado.
    """
    buf = _buffers.get(conn, b'')
    while b'\n' not in buf:
        chunk = conn.recv(1024)
        if not chunk:
            return None
        buf += chunk
    line, sep, rest = buf.partition(b'\n')
    _buffers[conn] = rest
    return line + sep

# gerenciamento de salas pendentes
rooms = {} # código -> Room
rooms_lock = threading.Lock()

class Room:
    """
    Sala temporária com dois jogadores
    """
    def __init__(self, code, creator_conn):
        self.code = code
        # socket do jogador que criou a sala
        self.creator = creator_conn
        # socket do jogador que entrou
        self.joiner = None
        # event sinalizando partida completa
        self.ready = threading.Event()


def generate_code(length=4):
    """Gera código alfanumérico para identificar a sala."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


def handle_client(conn, addr):
    """
    Thread de lobby para cada conexão
    """
    try:
        raw = recv_line(conn)
        if raw is None:
            conn.close()
            return
        t, content = unpack(raw)

        if t == MSG_TYPE['CREATE_ROOM']:
            # Cria nova sala e aguarda joiner
            code = generate_code()
            room = Room(code, conn)
            with rooms_lock:
                rooms[code] = room
            conn.send(pack(MSG_TYPE['ROOM_CREATED'], code))
            print(f"[Lobby] Sala {code} criada por {addr}, aguardando par...")
            room.ready.wait()
            # Inicia partida quando joiner chegar
            start_game(room.creator, room.joiner)
            with rooms_lock:
                del rooms[code]

        elif t == MSG_TYPE['JOIN_ROOM']:
            # Entra em sala existente, sinaliza criador
            code = content
            with rooms_lock:
                room = rooms.get(code)
            if not room:
                conn.send(pack(MSG_TYPE['ERROR'], 'Sala não encontrada.'))
                conn.close()
                return
            
            if room.joiner is not None:
                conn.send(pack(MSG_TYPE['ERROR'], 'Sala cheia.'))
                conn.close()
                return
            
            room.joiner = conn
            room.ready.set()
            conn.send(pack(MSG_TYPE['ROOM_JOINED'], code))
            room.creator.send(pack(MSG_TYPE['ROOM_JOINED'], code))
            print(f"[Lobby] Cliente {addr} entrou na sala {code}.")

        else:
            # Comando inesperado no lobby
            conn.send(pack(MSG_TYPE['ERROR'], 'Comando inválido no lobby.'))
            conn.close()

    except Exception as e:
        print(f"[Erro no lobby] {e}")
        conn.close()


def start_game(conn1, conn2):
    """
    Encapsula a partida usando Game
    """
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
    """
    Loop principal do servidor:
    - bind/listen
    - aceita conexões e dispara handle_client em thread
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        print(f"[Servidor] À escuta em {HOST}:{PORT}")
        while True:
            conn, addr = sock.accept()
            threading.Thread(
                target=handle_client,
                args=(conn, addr),
                daemon=True
            ).start()

if __name__ == '__main__':
    main()
