import json


# Dicionário de tipos de mensagem utilizados no protocolo cliente-servidor.
MSG_TYPE = {
    'SECRET': 'SECRET', # segredo que cada jogador escolhe
    'START': 'START',  # flag para o comeco do jogo
    'QUESTION': 'QUESTION',  # pergunta enviada 
    'ANSWER': 'ANSWER', # resposta da pergunta ("sim" ou "não")
    'GUESS': 'GUESS',  # palpite sobre o segredo adversário
    'RESULT': 'RESULT', # resultado do palpite (True/False)
    'TURN': 'TURN', # flag indicando qual jogador tem a vez
    'END': 'END' # encerra o jogo apos palpite correto
}

def pack(msg_type, content):
    # Empacota uma mensagem em JSON para envio pelo socket.
    return (json.dumps({'type': msg_type, 'content': content}) + '\n').encode()

def unpack(data):
    # Desempacota dados recebidos de um socket para obter tipo e conteúdo.
    text = data.decode().strip()
    # Considera apenas a primeira linha JSON
    first, *_ = text.split('\n')
    obj = json.loads(first)
    return obj['type'], obj['content']

