wordlist = ['have', 'that', 'with', 'this', 'that', 'they', 'what', 'from', 'know', 'your', 'about', 'their', 'will', 'would', 'make', 'just', 'think', 'time', 'there', 'come', 'take', 'year', 'them', 'some', 'want', 'when', 'which', 'like', 'other', 'could', 'here', 'then', 'than', 'look', 'more', 'these', 'thing', 'well', 'also', 'tell', 'good', 'first', 'find', 'give', 'more', 'those', 'very', 'need', 'back', 'there', 'even', 'only', 'many', 'work', 'life', 'right', 'down', 'call', 'woman', 'still', 'mean', 'after', 'never', 'world', 'feel', 'yeah', 'great', 'last', 'child', 'over', 'when', 'state', 'much', 'talk', 'keep', 'leave', 'like', 'help', 'where', 'same', 'while', 'start', 'three', 'high', 'every', 'most', 'over', 'house', 'show', 'again', 'seem', 'might', 'part', 'hear', 'place', 'where', 'week', 'point', 'hand', 'play', 'turn', 'group', 'such', 'about', 'case', 'work', 'night', 'live', 'game', 'write', 'bring', 'money', 'most', 'book', 'next', 'city', 'story', 'today', 'move', 'must', 'begin', 'love', 'each', 'hold', 'ever', 'word', 'fact', 'right', 'read', 'sure', 'small', 'month', 'maybe', 'right', 'under', 'home', 'kind', 'stop', 'study', 'since', 'name', 'room', 'away', 'large', 'lose', 'power', 'head', 'real', 'best', 'team', 'long', 'long', 'side', 'water', 'young', 'wait', 'okay', 'both', 'after', 'meet', 'area', 'thank', 'much', 'only', 'hour', 'four', 'line', 'girl', 'watch', 'until', 'learn', 'least', 'kill', 'party', 'stand', 'back', 'often', 'speak', 'black', 'once', 'news', 'allow', 'body', 'lead', 'spend', 'level', 'able', 'stay', 'later', 'five', 'among', 'face', 'food', 'else', 'send', 'walk', 'door', 'white', 'court', 'home', 'grow', 'open', 'both', 'such', 'late', 'free', 'table', 'sorry', 'care', 'human', 'hope', 'data', 'offer', 'death', 'whole', 'plan', 'easy', 'build', 'fall', 'hard', 'sense', 'show', 'early', 'music', 'mind', 'class', 'heart', 'serve', 'break', 'even', 'force', 'foot', 'agree', 'baby', 'wrong', 'love', 'full', 'pass', 'rate', 'local', 'sell', 'wife', 'value', 'base', 'pick', 'phone', 'event', 'drive', 'reach', 'site', 'pull', 'model', 'fine', 'movie', 'field', 'raise', 'less', 'light', 'role', 'view', 'price', 'nice', 'quite', 'along', 'voice', 'photo', 'wear', 'space', 'film', 'need', 'major', 'type', 'town', 'road', 'form', 'drug', 'cause', 'happy', 'join', 'teach', 'early', 'share', 'carry', 'clear', 'dead', 'star', 'cost', 'post', 'piece', 'paper', 'open', 'media', 'miss', 'save', 'catch', 'look', 'term', 'color', 'cover', 'guess', 'soon', 'rule', 'face', 'check', 'page', 'fight', 'test', 'half', 'video', 'throw', 'third', 'care', 'rest', 'step', 'ready', 'call', 'whose', 'less', 'shoot', 'list', 'stuff', 'risk', 'focus', 'short', 'fire', 'hair', 'point', 'wall', 'deal', 'truth', 'upon', 'order', 'close', 'land', 'note', 'goal', 'bank', 'sound', 'deal', 'north', 'well', 'blood', 'close', 'tree', 'park', 'draw', 'plan', 'drop', 'push', 'earth', 'cause', 'race', 'than', 'other', 'hell', 'poor', 'each', 'hard', 'song', 'enjoy', 'past', 'seek', 'store', 'bill', 'like', 'cell', 'away', 'board', 'fill', 'state', 'place', 'fail', 'help', 'mile', 'floor', 'vote', 'south', 'press', 'worry', 'enter', 'sound', 'thus', 'plant', 'scene', 'wish', 'west', 'claim', 'prove', 'sort', 'size', 'hang', 'sport', 'loss', 'argue', 'left', 'note', 'skill', 'card', 'crime', 'that', 'sign', 'occur', 'vote', 'near', 'king', 'seven', 'laugh', 'lady', 'ball', 'east', 'apply', 'huge', 'name', 'rise', 'force', 'sign', 'staff', 'hurt', 'legal', 'final', 'since', 'safe', 'dream', 'shit', 'eight', 'main', 'exist', 'dark', 'play', 'union', 'stage', 'blue', 'pain', 'avoid', 'fund', 'treat', 'shot', 'hate', 'visit', 'club', 'river', 'brain', 'rock', 'talk', 'best', 'close', 'date', 'army', 'post', 'seat']
import random

def get_random_word() -> str:
    """Returns a random word in lowercase"""
    return random.choice(wordlist).lower()

def get_random_word_string(words=2, seperate="pascal") -> str:
    """Generates a string containg the given amount of words.

    Available options for seperate:
    pascal: TwoWords
    dash: two-words"""

    result = ""

    if seperate == "pascal":
        # Add random words n times to the result in titlecase
        for _ in range(0, words):
            result += get_random_word().title()
    
    elif seperate == "dash":
        # Add random words n times to the result + a dash
        for _ in range(0, words):
            result += get_random_word().lower() + "-"
        # Removing the last added dash
        result = result[:-1]
    
    return result