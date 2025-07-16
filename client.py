import socket
import threading
from protocol import MSG_TYPE, pack, unpack

HOST = '127.0.0.1'
PORT = 5000
DUVIDA = 'D'

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
            if action == DUVIDA:
                q = input("Pergunta sim/não: ")
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

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        secret = input("Defina o que o outro deve adivinhar: ")
        sock.send(pack(MSG_TYPE['SECRET'], secret))
        threading.Thread(target=listen, args=(sock,), daemon=True).start()
        threading.Event().wait()

if __name__ == '__main__':
    main()
