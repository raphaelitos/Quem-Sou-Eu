import socket
import threading
import random
import string
from protocol import *
from game import Game

HOST = '0.0.0.0'
PORT = 5000

# Gerencia salas pendentes
rooms = {}             # código -> Room
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
        # Primeiro, recebe CREATE_ROOM ou JOIN_ROOM
        t, content = unpack(conn.recv(1024))
        if t == MSG_TYPE['CREATE_ROOM']:
            # cria sala nova
            code = generate_code()
            room = Room(code, conn)
            with rooms_lock:
                rooms[code] = room
            # envia confirmação com o código
            conn.send(pack(MSG_TYPE['ROOM_CREATED'], code))
            print(f"[Lobby] Sala {code} criada por {addr}, aguardando par...")
            # espera que alguém entre
            room.ready.wait()

            # quando pronto, inicia o jogo
            opponent_conn = room.joiner
            start_game(room.creator, opponent_conn)

            # remove sala
            with rooms_lock:
                del rooms[code]

        elif t == MSG_TYPE['JOIN_ROOM']:
            # tenta entrar em sala existente
            code = content
            with rooms_lock:
                room = rooms.get(code)
            if not room:
                conn.send(pack(MSG_TYPE['ERROR'], 'Sala não encontrada.'))
                conn.close()
                return
            # registra quem entrou e sinaliza
            room.joiner = conn
            room.ready.set()
            # confirma entrada
            conn.send(pack(MSG_TYPE['ROOM_JOINED'], code))
            print(f"[Lobby] Cliente {addr} entrou na sala {code}.")
            # criador vai receber ROOM_JOINED também imediatamente
            room.creator.send(pack(MSG_TYPE['ROOM_JOINED'], code))

            # o criador e o joiner serão passados para start_game pela thread do criador
        else:
            conn.send(pack(MSG_TYPE['ERROR'], 'Comando inválido no lobby.'))
            conn.close()
    except Exception as e:
        print(f"[Erro no lobby] {e}")
        conn.close()

def start_game(conn1, conn2):
    """Função que roda a partida usando sua classe Game."""
    try:
        game = Game(conn1, conn2)
        game.setup()
        # inicia turno do jogador 1
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
