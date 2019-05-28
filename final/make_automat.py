import json
import io
from state import state
from state import state_machine

alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ-'

def make_state_tree(dictionary):
    if not dictionary:
        return state()
    s = state()
    s.final = '' in dictionary
    for letter in alphabet:
        sub_dict = filter(lambda word: word.startswith(letter), dictionary)
        sub_dict = set(map(lambda word: word[1:], sub_dict))
        if sub_dict: # delete this validation for the sake of more saturated state machine
            s.gotos[letter] = make_state_tree(sub_dict)
    return s

words = []
with io.open('dict.txt', 'r', encoding='utf-8') as f:
    words = f.read()
    words = words.split()

print("make tree")
state_tree = make_state_tree(set(words))
print("make state machine")
sm = state_machine.from_tree(state_tree, alphabet)

print("make automat.json")
with io.open('automat.json', 'w', encoding='utf-8') as f:
    state_tree_json = state_tree.to_json()
    #print(state_tree_json)
    f.write(state_tree_json)

print("make sm.json")
with io.open('sm.json', 'w', encoding='utf-8') as f:
    sm_json = sm.to_json()
    #print(sm_json)
    f.write(sm_json)
