import json

# Define tipos de mensagem usados tanto no lobby quanto no jogo
MSG_TYPE = {
    # Lobby
    'CREATE_ROOM': 'CREATE_ROOM', # Cliente quer criar nova sala
    'ROOM_CREATED': 'ROOM_CREATED', # Servidor responde com código gerado
    'JOIN_ROOM': 'JOIN_ROOM', # Cliente quer entrar em sala existente
    'ROOM_JOINED': 'ROOM_JOINED', # Servidor confirma entrada na sala
    'ERROR': 'ERROR', # Erro (lobby ou jogo)
    'EXIT': 'EXIT', # Cliente decide sair
    # Jogo
    'SECRET': 'SECRET', # Segredo enviado por cada jogador
    'START': 'START', # Início do jogo com IDs you/opponent
    'QUESTION': 'QUESTION', # Pergunta sim/não enviada
    'ANSWER': 'ANSWER', # Resposta à pergunta
    'GUESS': 'GUESS', # Palpite sobre o segredo do oponente
    'RESULT': 'RESULT', # Resultado do palpite (True/False)
    'TURN': 'TURN', # Indica vez do jogador
    'END': 'END' # Encerramento da partida
}

def pack(msg_type, content):
    """
    Empacota tipo e conteúdo num JSON + '\n', para enviar via socket.
    """
    payload = {'type': msg_type, 'content': content}
    return (json.dumps(payload) + '\n').encode()


def unpack(data):
    """
    Extrai tipo e conteúdo de bytes JSON recebidos.
    Considera apenas até o primeiro '\n'.
    """
    text = data.decode().strip()
    first, *_ = text.split('\n')
    obj = json.loads(first)
    return obj['type'], obj['content']
