import socket
import threading
from protocol import *

HOST = '172.24.220.27'
PORT = 5000

# === framing por linha no cliente ===
_buffers = {}  # sock -> bytes

def recv_line(sock):
    buf = _buffers.get(sock, b'')
    while b'\n' not in buf:
        chunk = sock.recv(1024)
        if not chunk:
            return None
        buf += chunk
    line, sep, rest = buf.partition(b'\n')
    _buffers[sock] = rest
    return line + sep

def listen(sock, game_over_evt):
    """Thread que consome mensagens do servidor; sinaliza game_over_evt no END."""
    while True:
        raw = recv_line(sock)
        if raw is None:
            # conexão fechou inesperadamente
            game_over_evt.set()
            break

        t, content = unpack(raw)

        if t == MSG_TYPE['START']:
            you = content['you']

        elif t == MSG_TYPE['TURN']:
            action = input("Duvida (D) ou palpite (P)? ").strip().upper()
            if action == 'D':
                q = input("Pergunta (sim/não): ")
                sock.send(pack(MSG_TYPE['QUESTION'], q))
            else:
                g = input("Seu palpite: ")
                sock.send(pack(MSG_TYPE['GUESS'], g))

        elif t == MSG_TYPE['QUESTION']:
            ans = input(f"{content} (sim/não): ").strip().lower()
            sock.send(pack(MSG_TYPE['ANSWER'], ans))

        elif t == MSG_TYPE['ANSWER']:
            print("Resposta:", content)

        elif t == MSG_TYPE['RESULT']:
            print("Correto!" if content else "Incorreto")

        elif t == MSG_TYPE['END']:
            print("Fim de jogo:", content)
            game_over_evt.set()
            break

        elif t == MSG_TYPE['ERROR']:
            print("Erro:", content)
            game_over_evt.set()
            break

def lobby(sock):
    """Mostra o menu de criar/entrar sala. Retorna True para iniciar jogo, False para sair."""
    while True:
        print("\n=== MENU ===")
        print("1. Criar sala")
        print("2. Entrar em sala")
        print("3. Sair")
        opt = input("Escolha: ").strip()

        if opt == '1':
            sock.send(pack(MSG_TYPE['CREATE_ROOM'], None))
            raw = recv_line(sock)
            if raw is None:
                print("Servidor desconectou.")
                return False
            t, code = unpack(raw)
            if t == MSG_TYPE['ROOM_CREATED']:
                print(f"Sala criada! Código: {code}")
                print("Aguardando oponente...")
                raw2 = recv_line(sock)
                if raw2 is None:
                    print("Servidor desconectou.")
                    return False
                t2, _ = unpack(raw2)
                if t2 == MSG_TYPE['ROOM_JOINED']:
                    print("Oponente entrou! Iniciando partida...\n")
                    return True

        elif opt == '2':
            code = input("Código da sala: ").strip().upper()
            sock.send(pack(MSG_TYPE['JOIN_ROOM'], code))
            raw = recv_line(sock)
            if raw is None:
                print("Servidor desconectou.")
                return False
            t, content = unpack(raw)
            if t == MSG_TYPE['ROOM_JOINED']:
                print("Entrou na sala! Iniciando partida...\n")
                return True
            else:
                print("Erro ao entrar:", content)

        elif opt == '3':
            sock.send(pack(MSG_TYPE['EXIT'], None))
            return False

        else:
            print("Opção inválida.")

def play(sock):
    """Fluxo de jogo: envia SECRET e inicia thread de escuta até END."""
    secret = input("Defina o que o outro deve adivinhar: ")
    sock.send(pack(MSG_TYPE['SECRET'], secret))

    game_over = threading.Event()
    t = threading.Thread(target=listen, args=(sock, game_over), daemon=True)
    t.start()

    # aguarda sinal de END ou ERROR na thread de escuta
    game_over.wait()

def main():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((HOST, PORT))

            if not lobby(sock):
                print("Saindo...")
                break

            play(sock)
            print("\n--- Retornando ao menu ---\n")

if __name__ == '__main__':
    main()
