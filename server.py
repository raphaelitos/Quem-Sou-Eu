import socket
from game import Game
from protocol import *

# Configuração de endereço e porta TCP onde o servidor escutara'
HOST = '0.0.0.0'
PORT = 5000

def main():
    # Cria um socket TCP IPv4 e garante seu fechamento ao final
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        # socket em modo de escuta aguarda até 2 conexões
        s.listen(2)
        
        # Aceita conexoes de cada jogador ignorando o endereço
        conn1, _ = s.accept()
        conn2, _ = s.accept()
        
        # Inicializa o objeto de jogo com as duas conexões
        game = Game(conn1, conn2)
        game.setup()
        # Primeira rodada e' feita explicitamente para o Jogador 1
        game.send(1, MSG_TYPE['TURN'], None)
        game.loop()
        
        # Fecha as conexões após o término do jogo
        conn1.close()
        conn2.close()

if __name__ == '__main__':
    main()
