import json

MSG_TYPE = {
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
    obj = json.loads(data.decode().strip())
    return obj['type'], obj['content']
