from protocol import *

MAX_PALPITES = 3

class Game:
    def __init__(self, conn1, conn2):
        self.conns = {1: conn1, 2: conn2}
        self.secrets = {}
        self.guesses = {1: 0, 2: 0}
        self.current = 1
        self._buffers = {1: b'', 2: b''}

    def recv(self, pid):
        conn = self.conns[pid]
        buf = self._buffers[pid]
        while b'\n' not in buf:
            chunk = conn.recv(1024)
            if not chunk:
                raise ConnectionError("Jogador desconectou")
            buf += chunk
        line, sep, rest = buf.partition(b'\n')
        self._buffers[pid] = rest
        return unpack(line + sep)

    def send(self, pid, msg_type, content):
        self.conns[pid].send(pack(msg_type, content))

    def other(self, pid):
        return 2 if pid == 1 else 1

    def setup(self):
        for pid in (1, 2):
            t, secret = self.recv(pid)
            if t != MSG_TYPE['SECRET']:
                raise ValueError("Esperava SECRET")
            self.secrets[pid] = secret
        for pid in (1, 2):
            self.send(pid, MSG_TYPE['START'], {'you': pid, 'opponent': self.other(pid)})

    def loop(self):
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
                if content == self.secrets[opp]:
                    self.send(pid, MSG_TYPE['RESULT'], True)
                    self.send(opp, MSG_TYPE['END'], f"Oponente adivinhou {content}")
                    break
                else:
                    self.send(pid, MSG_TYPE['RESULT'], False)
                    if self.guesses[pid] >= MAX_PALPITES:
                        self.send(pid, MSG_TYPE['END'], "Muitos palpites incorretos :(")
                        self.send(opp, MSG_TYPE['END'], "Você venceu! Seu oponente atingiu o limite de palpites :)")
                        break

            self.current = opp
            self.send(self.current, MSG_TYPE['TURN'], None)
