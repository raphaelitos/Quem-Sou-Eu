import socket
import threading
from protocol import *

HOST = '172.24.220.27'  # IP do servidor
PORT = 5000

def listen(sock):
    while True:
        data = sock.recv(1024)
        if not data:
            break
        t, content = unpack(data)

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
            break

        elif t == MSG_TYPE['ERROR']:
            print("Erro:", content)
            break

def lobby(sock):
    while True:
        print("\n=== MENU ===")
        print("1. Criar sala")
        print("2. Entrar em sala")
        print("3. Sair")
        opt = input("Escolha: ").strip()

        if opt == '1':
            sock.send(pack(MSG_TYPE['CREATE_ROOM'], None))
            t, code = unpack(sock.recv(1024))
            if t == MSG_TYPE['ROOM_CREATED']:
                print(f"Sala criada! Código: {code}")
                print("Aguardando oponente...")
                # espera confirmação de ROOM_JOINED
                t2, _ = unpack(sock.recv(1024))
                if t2 == MSG_TYPE['ROOM_JOINED']:
                    print("Oponente entrou! Iniciando partida...\n")
                    return True

        elif opt == '2':
            code = input("Código da sala: ").strip().upper()
            sock.send(pack(MSG_TYPE['JOIN_ROOM'], code))
            t, content = unpack(sock.recv(1024))
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

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))

        if not lobby(sock):
            print("Saindo...")
            return

        # segue o fluxo original
        secret = input("Defina o que o outro deve adivinhar: ")
        sock.send(pack(MSG_TYPE['SECRET'], secret))

        threading.Thread(target=listen, args=(sock,), daemon=True).start()
        threading.Event().wait()

if __name__ == '__main__':
    main()
