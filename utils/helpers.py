import random

def pick_random_word(words):
    return random.choice(words)

def format_choices(choices):
    return "\n".join([f"{i+1}. {c}" for i,c in enumerate(choices)])

