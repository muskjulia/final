from state import state_machine

def incount_rec(sm, current_state, res={}):
    if not sm.transitions.__contains__(current_state):
        return res

    for letter, gotos in sm.transitions[current_state].items():
        next_state = next(iter(gotos))
        res.setdefault(next_state, {})[letter] = 1
        res = incount_rec(sm, next_state, res)
    return res

def incount(sm):
    current_state=next(iter(sm.start_states))
    res = incount_rec(sm, current_state)
    return dict(map(lambda entry: (entry[0], sum(entry[1].values())), res.items()))


def outcount(sm):
    return dict(map(lambda entry: (entry[0], len(entry[1])), sm.transitions.items()))


def rcount_rec(sm, current_state, res={}):
    rc = int(sm.final_states.__contains__(current_state))

    for _, gotos in sm.transitions.get(current_state, {}).items():
        next_state = next(iter(gotos))
        res = rcount_rec(sm, next_state, res)
        rc += res[next_state]

    res[current_state] = rc

    return res

def rcount(sm):
    current_state=next(iter(sm.start_states))
    res = rcount_rec(sm, current_state)
    return res

def word_analyzer_rec(sm, inc, outc, rc, current_state, word, res=[]):
    res.append({
        'state': current_state,
        'final': sm.final_states.__contains__(current_state),
        'incount': inc.get(current_state, 0),
        'outcount': outc.get(current_state, 0),
        'rcount': rc.get(current_state, 0)
    })
    if word and sm.transitions.__contains__(current_state) and sm.transitions[current_state].__contains__(word[0]):
        res.append(word[:1])
        res = word_analyzer_rec(sm, inc, outc, rc, next(iter(sm.transitions[current_state][word[:1]])), word[1:], res)
    return res


def word_analyzer(sm, word):
    current_state = next(iter(sm.start_states))
    inc = incount(sm)
    outc = outcount(sm)
    rc = rcount(sm)

    return word_analyzer_rec(sm, inc, outc, rc, current_state, word)

with open('sm.json', 'r', encoding='utf-8') as f:
    sm = f.read()
    sm = state_machine.from_json(sm)
    print(sm.to_json())

    inc = incount(sm)
    print(inc)

    outc = outcount(sm)
    print(outc)

    rc = rcount(sm)
    print(rc)

    with open("dict.txt", 'r', encoding='utf-8') as words:
        for word in words:
            with open('metrics.json', 'w', encoding='utf-8') as metrics:
                analyzed_word = str(word_analyzer(sm, word)).replace('\'', '\"').replace('True', 'true').replace('False', 'false')
                print(analyzed_word)
                metrics.write(analyzed_word + '\n')