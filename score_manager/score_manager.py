'''manage score and store on json file'''
import json
SCORE_FILE = 'scores.json'

def read_file():
    '''read a file from scores.json'''
    try:
        with open(SCORE_FILE, 'r', encoding='UTF-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save(scores):
    '''save score to a file'''
    with open(SCORE_FILE, 'w', encoding='UTF-8') as file:
        json.dump(scores, file)

def add_score(user, score):
    '''add score to player'''
    scores = read_file()
    scores[str(user)] = scores.get(str(user), 0) + score
    save(scores)
