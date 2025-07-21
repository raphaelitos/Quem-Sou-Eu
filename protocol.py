import json

MSG_TYPE = {
    # Lobby
    'CREATE_ROOM': 'CREATE_ROOM',
    'ROOM_CREATED': 'ROOM_CREATED',
    'JOIN_ROOM': 'JOIN_ROOM',
    'ROOM_JOINED': 'ROOM_JOINED',
    'ERROR': 'ERROR',
    'EXIT': 'EXIT',
    # Jogo
    'SECRET': 'SECRET',
    'START': 'START',
    'QUESTION': 'QUESTION',
    'ANSWER': 'ANSWER',
    'GUESS': 'GUESS',
    'RESULT': 'RESULT',
    'TURN': 'TURN',
    'END': 'END'
}

def pack(msg_type, content):
    return (json.dumps({'type': msg_type, 'content': content}) + '\n').encode()

def unpack(data):
    text = data.decode().strip()
    first, *_ = text.split('\n')
    obj = json.loads(first)
    return obj['type'], obj['content']
