import json
import io
from state import state
from state import state_machine

alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

def make_state_tree(dictionary):
    if not dictionary:
        return state()
    s = state()
    s.final = '' in dictionary
    for letter in alphabet:
        sub_dict = filter(lambda word: word.startswith(letter), dictionary)
        sub_dict = list(map(lambda word: word[1:], sub_dict))
        if sub_dict: # delete this validation for the sake of more saturated state machine
            s.gotos[letter] = make_state_tree(sub_dict)
    return s

words = []
with io.open('dict.txt', 'r', encoding='utf-8') as f:
    words = f.read()
    words = words.split()
 
state_tree = make_state_tree(words)
sm = state_machine.from_tree(state_tree, alphabet)

with io.open('automat.json', 'w', encoding='utf-8') as f:
    print(state_tree.to_json())
    f.write(state_tree.to_json())

with io.open('sm.json', 'w', encoding='utf-8') as f:
    print(sm.to_json())
    f.write(sm.to_json())
