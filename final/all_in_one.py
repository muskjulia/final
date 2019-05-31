from state import state_machine
from state import state

import config
import time
import json
import io

################## dict_to_dic ##################

new_dict = []
with open('dict.original.txt', 'r', encoding='utf-8') as f:
    count = 0
    nth = 100
    group = 40
    for line in f:
        if '\t' in line and (count // group % nth) == 0:
            word = line[0:line.find('\t')] # substring from 0 to the '\t' position
            if not any((d in word) for d in '0123456789'):
                new_dict.append(config.FNREV(word) + '\n')
        count += 1

################## beautifier ##################

words = new_dict
words = list(set(words))
words.sort()
new_dict = words

################## make_automat ##################

alphabet = config.ALPHABET

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

words = new_dict

print("make tree")
state_tree = make_state_tree(set(words))
print(words)
print(state_tree.to_json())
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

################## minimize ##################

alphabet = config.ALPHABET

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
                
    return sm

s = state_tree
sm = minimize(s)
print(s.to_json())
print(sm.to_json())
with open ('sm-min.json', 'w', encoding='utf-8') as outf:
    print(sm.to_json(), file=outf)

################## metrics ##################

def incount_rec(sm, current_state, res):
    if not sm.transitions.__contains__(current_state):
        return res

    for letter, gotos in sm.transitions[current_state].items():
        next_state = next(iter(gotos))
        res.setdefault(next_state, {})[letter] = 1
        res = incount_rec(sm, next_state, res)
    return res

def incount(sm):
    current_state=next(iter(sm.start_states))
    res = incount_rec(sm, current_state, {})
    return dict(map(lambda entry: (entry[0], sum(entry[1].values())), res.items()))


def outcount(sm):
    return dict(map(lambda entry: (entry[0], len(entry[1])), sm.transitions.items()))


def rcount_rec(sm, current_state, res):
    rc = int(sm.final_states.__contains__(current_state))

    for _, gotos in sm.transitions.get(current_state, {}).items():
        next_state = next(iter(gotos))
        res = rcount_rec(sm, next_state, res)
        rc += res[next_state]

    res[current_state] = rc

    return res

def rcount(sm):
    current_state=next(iter(sm.start_states))
    res = rcount_rec(sm, current_state, {})
    return res

KEYS = ('final',
        'incount',
        'outcount',
        'lcount',
        'rcount',
        'rcountrel',
        'lcountrel',
        'rlcount'
        )

def word_analyzer_rec(sm, inc, outc, rc, current_state, word, res):
    info = {
        'state': current_state,
        'final': 1 if sm.final_states.__contains__(current_state) else 0,
        'incount': inc.get(current_state, 0),
        'outcount': outc.get(current_state, 0),
        'rcount': rc.get(current_state, 0),
        'lcount': len(lc.get(current_state, set()))
    }
    info['rlcount'] = info['rcount'] * info['lcount']
    res.append(info)
    if (word
        and sm.transitions.__contains__(current_state)
        and sm.transitions[current_state].__contains__(word[0])):
        res.append(word[:1])
        res = word_analyzer_rec(sm, inc, outc, rc,
                                next(iter(sm.transitions[current_state][word[:1]])),
                                word[1:], res)
    return res

def word_analyzer(sm, word):
    current_state = next(iter(sm.start_states))

    analyzed = word_analyzer_rec(sm, inc, outc, rc, current_state, word, [])

    analyzed[0]['rcountrel'] = 1.0
    for i in range(len(analyzed) // 2):
        if analyzed[2*i + 2]['rcount']:
            analyzed[2*i + 2]['rcountrel'] = \
                round(analyzed[2*i]['rcount'] / analyzed[2*i+2]['rcount'], 3)
        else:
            analyzed[2*i + 2]['rcountrel'] = 100500

    analyzed[0]['lcountrel'] = 1.0
    for i in range(len(analyzed) // 2):
        if analyzed[2*i]['lcount']:
            analyzed[2*i + 2]['lcountrel'] = \
                round(analyzed[2*i+2]['lcount'] / analyzed[2*i]['lcount'], 3)
        else:
            analyzed[2*i + 2]['lcountrel'] = analyzed[2*i + 2]['lcount']
    return analyzed

def lcount_update(sm, word, res):
    current_state = next(iter(sm.start_states))

    for i in range(len(word)):
        if (sm.transitions.__contains__(current_state)
                and sm.transitions[current_state].__contains__(word[i])):
            current_state = next(iter(sm.transitions[current_state][word[i]]))
            res.setdefault(current_state, set()).add(word[:i])

def lcount(sm):
    res = {}
    with open("dict.txt", 'r', encoding='utf-8') as words:
        for word in words:
            lcount_update(sm, word, res)
    return res

def str_state(state):
    return "<{state},{final},{incount},{outcount},{rcount},{rcountrel}>".format(**state)

THRESHOLD = { 'incount' : 1,
              'final' : 0.5,
              'outcount' : 1,
              'rcount' : 1,
              'rcountrel' : 1.0,
              'lcount' : 1,
              'lcountrel' : 1.0,
              }

def str_state_key(state, key):
    if not THRESHOLD.get(key) or state[key] > THRESHOLD[key]:
        return " <{0}:{1}> ".format(state['state'], state[key])
    else:
        return ""

with open("trace.txt", 'w', encoding='utf-8') as trace:
    print(sm.to_json(), file=trace)

    print("incount…")
    inc = incount(sm)
    print(inc, file=trace)

    print("outcount…")
    outc = outcount(sm)
    print(outc, file=trace)

    print("rcount…")
    rc = rcount(sm)
    print(rc, file=trace)

    print("lcount…")
    print(file=trace)
    lc = lcount(sm)
    print(lc, file=trace)

    print("analyzing…")
    analyzed_words = []
    with open("dict.txt", 'r', encoding='utf-8') as words:
        for word in words:
            if len(analyzed_words) % 10000 == 0:
                print(time.asctime(), len(analyzed_words))
            analyzed_word = config.FNREV(word_analyzer(sm, word))
            analyzed_words.append(analyzed_word)
    analyzed_words.sort(key = lambda word: ''.join(word[1::2]))

    print("output to files…")
    targets = {}
    for key in KEYS:
        targets[key] = open(config.PREFIX + "metric-" + key + ".txt",
                            "w", encoding='utf-8')
    
    with open('metrics.json', 'w', encoding='utf-8') as metrics \
       , open(config.PREFIX + 'metrics.txt', 'w', encoding='utf-8') as metrics_txt:
        for analyzed_word in analyzed_words:
            line = ''
            for p in analyzed_word:
                if type(p) is dict:
                    line += str_state(p)
                else:
                    line += p
            print(line, file=metrics_txt)

            for key in KEYS:
                line = ''.join(analyzed_word[1::2]) + ': '
                for p in analyzed_word:
                    if type(p) is dict:
                        line += str_state_key(p, key)
                    else:
                        line += p
                print(line, file=targets[key])

            analyzed_word = str(analyzed_word) \
                            .replace('\'', '\"') \
                            .replace('True', 'true') \
                            .replace('False', 'false')
            #print(analyzed_word)
            metrics.write(analyzed_word + '\n')

    for key in KEYS:
        targets[key].close()
