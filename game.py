from protocol import MSG_TYPE, pack, unpack

class Game:
    def __init__(self, conn1, conn2):
        self.conns = {1: conn1, 2: conn2}
        self.secrets = {}
        self.guesses = {1: 0, 2: 0}
        self.current = 1

    def recv(self, pid):
        data = self.conns[pid].recv(1024)
        return unpack(data)

    def send(self, pid, msg_type, content):
        self.conns[pid].send(pack(msg_type, content))

    def other(self, pid):
        return 2 if pid == 1 else 1

    def setup(self):
        for pid in (1, 2):
            t, secret = self.recv(pid)
            if t != MSG_TYPE['SECRET']:
                raise ValueError
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
                guess = content
                if guess == self.secrets[opp]:
                    self.send(pid, MSG_TYPE['RESULT'], True)
                    self.send(opp, MSG_TYPE['END'], f"Opponent guessed {guess}")
                    break
                else:
                    ok = False
                    self.send(pid, MSG_TYPE['RESULT'], False)
            self.current = opp
            self.send(self.current, MSG_TYPE['TURN'], None)
