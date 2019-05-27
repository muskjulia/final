from state import state
from state import state_machine
import io

alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

# def rev(sm):
#     rsm = state_machine()
#     rsm.start_states = sm.final_states
#     rsm.final_states = sm.start_states
#     rsm.states = sm.states
#     rsm.alphabet = sm.alphabet
    
#     for from_state in sm.transitions:
#         for letter in sm.transitions[from_state]:
#             to_state_set = sm.transitions[from_state][letter]
#             for to_state in to_state_set:
#                 rsm.transitions.setdefault(to_state, {}).setdefault(letter, set()).add(from_state)
#     return rsm

# def reachable(sm, q, state_id):
#         state_transitions = {}
#         for letter in sm.alphabet:
#             endpoints_subset = set()
#             for new_state_id in q[state_id]:
#                 endpoints_subset |= sm.transitions.get(new_state_id, {}).get(letter, set())
#             if not endpoints_subset:
#                 continue
#             try:
#                 new_state_id = q.index(endpoints_subset)
#             except ValueError:
#                 new_state_id = len(q)
#                 q.append(endpoints_subset)
#             state_transitions[letter] = set([new_state_id])
#         return q, state_transitions

# def det(sm):
#     dsm = state_machine()
#     dsm.alphabet = sm.alphabet
#     dsm.start_states = {0}
    
#     state_id = 0
#     q = [set(sm.start_states)]
#     while state_id < len(q):
#         q, dsm.transitions[state_id] = reachable(sm, q, state_id)
#         state_id += 1
        
#     dsm.states = set(range(0, len(q)))
#     dsm.final_states = set([q.index(i) for i in q if set(sm.final_states) & i])

#     return dsm

# def brzozovski(sm):
#     return det(rev(det(rev(sm))))

# with io.open('automat.json', 'r', encoding='utf-8') as f:
#     raw = f.read()
#     s = state.from_json(raw)

# with io.open('sm.json', 'r', encoding='utf-8') as f:
#     raw = f.read()
#     sm = state_machine.from_json(raw)

# sm1 = state_machine.from_tree(s, alphabet)
# print(sm.to_json())
# print(sm1.to_json())

# sm = minimize(sm)
# print(sm.to_json())

# with io.open('sm.json', 'w', encoding='utf-8') as f:
#     raw = f.write(sm.to_json())


def rec(state, res):
    sign = [state.final]
    for letter in alphabet:
        if state.gotos.__contains__(letter):
            next_sign, res = rec(state.gotos[letter], res)
            sign.append(res[next_sign])
        else:
            sign.append(None)
    sign = tuple(sign)

    if not res.__contains__(sign):
        res[sign] = len(res)

    return sign, res

def minimize(start_state):
    start_state, res = rec(start_state, {})

    new_id = lambda x: len(res) - x - 1

    sm = state_machine()
    sm.alphabet = alphabet
    sm.start_states = {new_id(res[start_state])}
    sm.states = res.values()

    for sign, state_id in res.items():
        state_id = new_id(state_id)
        sign = list(map(lambda a: new_id(a) if type(a) == int else a, sign))

        if sign[0]:
            sm.final_states.add(state_id)
        
        for i in range(0, len(alphabet)):
            if sign[i + 1] != None:
                sm.transitions.setdefault(state_id, {}).setdefault(alphabet[i], set()).add(sign[i + 1])

    
    # res = dict(map(lambda elem: (tuple(map(lambda a: len(res) - a - 1 if type(a) == int else a, elem[0])), len(res) - elem[1] - 1), res.items()))
    # start_state = tuple(map(lambda a: len(res) - a - 1 if type(a) == int else a, start_state))

    # sm = state_machine()
    # sm.alphabet = alphabet
    # sm.states = set(res.values())
    # sm.start_states = {res[start_state]}
    # sm.final_states = set(map(lambda elem: elem[1], filter(lambda elem: elem[0][0], res.items())))
    # sm.transitions = dict(map(lambda elem: (elem[1], dict(filter(lambda state_id: state_id != None, map(lambda i: None if elem[0][i + 1] == None else (alphabet[i], {elem[0][i + 1]}), range(len(alphabet)))))), res.items()))

    return sm

with io.open('automat.json', 'r', encoding='utf-8') as f:
    raw = f.read()
    s = state.from_json(raw)
    
    sm = minimize(s)
    print(sm.to_json())
