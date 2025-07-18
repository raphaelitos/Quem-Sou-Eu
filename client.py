import socket
import threading
from protocol import *

# Endereço e porta do servidor TCP
HOST = '172.24.220.27'   # IP da Máquina A
PORT = 5000
DUVIDA = 'D'

def listen(sock):
    
    #Loop dedicado para receber e processar mensagens do servidor
    #Executado em thread separada para não bloquear o envio de dados
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
    # Cria socket TCP e conecta no servidor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        
        # Envia o segredo que o adversário deve adivinhar
        secret = input("Defina o que o outro deve adivinhar: ")
        sock.send(pack(MSG_TYPE['SECRET'], secret))
        
        # Inicia thread de escuta para processar mensagens recebidas
        threading.Thread(target=listen, args=(sock,), daemon=True).start()
        
        # thread principal contnua viva
        threading.Event().wait()

if __name__ == '__main__':
    main()
