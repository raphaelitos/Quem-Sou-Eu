import json

# Dicionário de tipos de mensagem utilizados no protocolo cliente-servidor.
MSG_TYPE = {
    # Lobby
    'CREATE_ROOM': 'CREATE_ROOM',   # pedido para criar uma sala
    'ROOM_CREATED': 'ROOM_CREATED', # confirmação com código gerado
    'JOIN_ROOM': 'JOIN_ROOM',       # pedido para entrar em sala existente
    'ROOM_JOINED': 'ROOM_JOINED',   # confirmação de entrada na sala
    'ERROR': 'ERROR',               # erro no lobby ou no jogo
    'EXIT': 'EXIT',                 # saída voluntária

    # Jogo
    'SECRET': 'SECRET',   # segredo que cada jogador escolhe
    'START': 'START',     # flag para o começo do jogo
    'QUESTION': 'QUESTION',   # pergunta enviada 
    'ANSWER': 'ANSWER',       # resposta da pergunta ("sim" ou "não")
    'GUESS': 'GUESS',         # palpite sobre o segredo adversário
    'RESULT': 'RESULT',       # resultado do palpite (True/False)
    'TURN': 'TURN',           # flag indicando qual jogador tem a vez
    'END': 'END'              # encerra o jogo após palpite correto ou limite
}

def pack(msg_type, content):
    """Empacota uma mensagem em JSON para envio pelo socket."""
    return (json.dumps({'type': msg_type, 'content': content}) + '\n').encode()

def unpack(data):
    """Desempacota dados recebidos de um socket para obter tipo e conteúdo."""
    text = data.decode().strip()
    first, *_ = text.split('\n')
    obj = json.loads(first)
    return obj['type'], obj['content']
