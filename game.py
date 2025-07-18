from protocol import *

MAX_PALPITES = 3

class Game:
    def __init__(self, conn1, conn2):
        # Mapeia IDs de jogador para as conexões de socket correspondentes
        self.conns = {1: conn1, 2: conn2}
        # Armazena o segredo de cada jogador
        self.secrets = {}
        # Contador de palpites realizados por cada jogador
        self.guesses = {1: 0, 2: 0}
        # Indica de quem e' a vez
        self.current = 1

    def recv(self, pid):
        # Lê dados do socket do jogador pid e desempacota
        data = self.conns[pid].recv(1024)
        return unpack(data)

    def send(self, pid, msg_type, content):
        # Empacota e envia mensagem para o jogador pid
        self.conns[pid].send(pack(msg_type, content))

    def other(self, pid):
        # Retorna o ID do adversário
        return 2 if pid == 1 else 1

    def setup(self):
        # Recebe o segredo de cada jogador
        # Envia mensagem START definindo IDs de you e opponent
        for pid in (1, 2):
            t, secret = self.recv(pid)
            if t != MSG_TYPE['SECRET']:
                raise ValueError
            self.secrets[pid] = secret
        for pid in (1, 2):
            self.send(pid, MSG_TYPE['START'], {'you': pid, 'opponent': self.other(pid)})

    def loop(self):
        
        # Alterna turnos
        # Processa perguntas (QUESTION) e palpites (GUESS)
        # Envia respostas, resultados e notifica fim de jogo
        while True:
            pid = self.current
            t, content = self.recv(pid)
            opp = self.other(pid)
            
            if t == MSG_TYPE['QUESTION']:
                self.send(opp, MSG_TYPE['QUESTION'], content)
                _, ans = self.recv(opp)
                self.send(pid, MSG_TYPE['ANSWER'], ans)
            
            elif t == MSG_TYPE['GUESS']:
                self.guesses[pid] += 1
                guess = content
                if guess == self.secrets[opp]:
                    self.send(pid, MSG_TYPE['RESULT'], True)
                    self.send(opp, MSG_TYPE['END'], f"Oponente adivinhou {guess}")
                    break
                else: # palpite errado
                    self.send(pid, MSG_TYPE['RESULT'], False)
                    if self.guesses[pid] >= MAX_PALPITES:
                        # Encerra jogo por excesso de erros
                        self.send(pid, MSG_TYPE['END'], "Muitos palpites incorretos :(")
                        self.send(opp, MSG_TYPE['END'], "Voce venceu! Seu oponente atingiu o limite de palpites :)")
                        break
            self.current = opp
            self.send(self.current, MSG_TYPE['TURN'], None)
