from protocol import *

MAX_PALPITES = 3

class Game:
    """
    Gerencia turnos, envia/recebe mensagens e finaliza o jogo.
    """
    def __init__(self, conn1, conn2):
        self.conns = {1: conn1, 2: conn2} # sockets de cada jogador: {1: conn1, 2: conn2}
        self.secrets = {} # segredos definidos por cada jogador
        self.guesses = {1: 0, 2: 0}  # contagem de palpites errados
        self.current = 1 # jogador que começa
        self._buffers = {1: b'', 2: b''} # buffers para leitura por linha em cada conexão

    def recv(self, pid):
        """
        Lê do socket do jogador pid até encontrar '\n' e
        mantém bytes excedentes no buffer
        Retorna (tipo, conteúdo) desempacotado
        """
        conn = self.conns[pid]
        buf = self._buffers[pid]
        # acumula até formar uma linha completa
        while b'\n' not in buf:
            chunk = conn.recv(1024)
            if not chunk:
                raise ConnectionError("Jogador desconectou")
            buf += chunk
        # separa linha lida do restante
        line, sep, rest = buf.partition(b'\n')
        self._buffers[pid] = rest
        return unpack(line + sep)

    def send(self, pid, msg_type, content):
        """
        Empacota e envia mensagem JSON ao jogador pid.
        """
        self.conns[pid].send(pack(msg_type, content))

    def other(self, pid):
        """
        Retorna o ID do oponente (1 <-> 2).
        """
        return 2 if pid == 1 else 1

    def setup(self):
        """
        Recebe o segredo de cada jogador e envia mensagem START,
        que inclui quem é 'you' e quem é 'opponent'.
        """
        for pid in (1, 2):
            t, secret = self.recv(pid)
            if t != MSG_TYPE['SECRET']:
                raise ValueError("Esperava SECRET")
            self.secrets[pid] = secret
        # informa IDs aos jogadores
        for pid in (1, 2):
            self.send(pid, MSG_TYPE['START'], {'you': pid, 'opponent': self.other(pid)})

    def loop(self):
        """
        Loop principal do jogo
        """
        while True:
            pid = self.current
            t, content = self.recv(pid)
            opp = self.other(pid)

            if t == MSG_TYPE['QUESTION']:
                # envia a pergunta ao oponente e recebe a resposta
                self.send(opp, MSG_TYPE['QUESTION'], content)
                _, ans = self.recv(opp)
                self.send(pid, MSG_TYPE['ANSWER'], ans)

            elif t == MSG_TYPE['GUESS']:
                # conta palpite e verifica acerto
                self.guesses[pid] += 1
                if content == self.secrets[opp]:
                    self.send(pid, MSG_TYPE['RESULT'], True)
                    self.send(opp, MSG_TYPE['END'], f"Oponente adivinhou {content}")
                    break
                else:
                    self.send(pid, MSG_TYPE['RESULT'], False)
                    # se estourar limite, encerra com derrota/vitória
                    if self.guesses[pid] >= MAX_PALPITES:
                        self.send(pid, MSG_TYPE['END'], "Muitos palpites incorretos :(")
                        self.send(opp, MSG_TYPE['END'], "Você venceu! Seu oponente atingiu o limite de palpites :)")
                        break

            # prepara próximo turno e avisa
            self.current = opp
            self.send(self.current, MSG_TYPE['TURN'], None)
