import socket
import threading
from protocol import *

HOST = '172.24.220.27'
PORT = 5000

_buffers = {}  # mapeia cada socket ao buffer de bytes pendentes

def recv_line(sock):
    """
    Lê do socket até encontrar um '\n', mantendo o que sobrar em _buffers.
    Retorna linha completa (incluindo '\n') ou None se conexão fechada.
    """
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
    """
    Thread que consome mensagens JSON do servidor.
    Sinaliza game_over_evt quando recebe END ou erro.
    """
    while True:
        raw = recv_line(sock)
        if raw is None:
            # conexão caiu antes do esperado
            game_over_evt.set()
            break

        t, content = unpack(raw)

        if t == MSG_TYPE['START']:
            # recebe IDs do jogador (you/opponent)
            you = content['you']

        elif t == MSG_TYPE['TURN']:
            action = input("Duvida (D) ou palpite (P)? ").strip().upper()
            if action == 'D':
                q = input("Pergunta (S/N): ")
                sock.send(pack(MSG_TYPE['QUESTION'], q))
            else:
                g = input("Seu palpite: ")
                sock.send(pack(MSG_TYPE['GUESS'], g))

        elif t == MSG_TYPE['QUESTION']:
            # servidor encaminha pergunta do oponente
            ans = input(f"{content} (S/N): ").strip().lower()
            sock.send(pack(MSG_TYPE['ANSWER'], ans))

        elif t == MSG_TYPE['ANSWER']:
            print("Resposta:", content)

        elif t == MSG_TYPE['RESULT']:
            # resultado do palpite enviado
            print("Correto!" if content else "Incorreto")

        elif t == MSG_TYPE['END']:
            # partida finalizada
            print("\nFim de jogo:", content)
            game_over_evt.set()
            break

        elif t == MSG_TYPE['ERROR']:
            # erros de lobby ou protocolo
            print("Erro:", content)
            game_over_evt.set()
            break

def lobby(sock):
    """
    Exibe menu de criar/entrar sala.
    Retorna True se usuário iniciou partida, False para sair.
    """
    while True:
        print("\n=== MENU ===")
        print("1. Criar sala")
        print("2. Entrar em sala")
        print("3. Sair")
        opt = input("Escolha: ").strip()

        if opt == '1':
            # criar nova sala
            sock.send(pack(MSG_TYPE['CREATE_ROOM'], None))
            raw = recv_line(sock)
            if raw is None:
                print("Servidor desconectou.")
                return False
            t, code = unpack(raw)
            if t == MSG_TYPE['ROOM_CREATED']:
                print(f"Sala criada! Código: {code}")
                print("Aguardando oponente...")
                # aguarda confirmação de entrada do oponente
                raw2 = recv_line(sock)
                if raw2 is None:
                    print("Servidor desconectou.")
                    return False
                t2, _ = unpack(raw2)
                if t2 == MSG_TYPE['ROOM_JOINED']:
                    print("Oponente entrou! Iniciando partida...\n")
                    return True

        elif opt == '2':
            # entrar em sala existente
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
            # sair do programa
            sock.send(pack(MSG_TYPE['EXIT'], None))
            return False

        else:
            print("Opção inválida.")

def play(sock):
    """
    Inicia partida: envia SECRET e aguarda END via listen().
    """
    secret = input("Defina o que o outro deve adivinhar: ")
    sock.send(pack(MSG_TYPE['SECRET'], secret))

    game_over = threading.Event()
    t = threading.Thread(target=listen, args=(sock, game_over), daemon=True)
    t.start()

    # bloqueia até evento de fim de jogo
    game_over.wait()


def main():
    """
    Loop principal: conecta, exibe lobby, executa play() e repete.
    """
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
