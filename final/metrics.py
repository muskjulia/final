from state import state_machine

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

KEYS = ('final', 'incount', 'outcount', 'rcount', 'rcountrel')

def word_analyzer_rec(sm, inc, outc, rc, current_state, word, res):
    res.append({
        'state': current_state,
        'final': 1 if sm.final_states.__contains__(current_state) else 0,
        'incount': inc.get(current_state, 0),
        'outcount': outc.get(current_state, 0),
        'rcount': rc.get(current_state, 0)
    })
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
    inc = incount(sm)
    outc = outcount(sm)
    rc = rcount(sm)

    analyzed = word_analyzer_rec(sm, inc, outc, rc, current_state, word, [])
    analyzed[0]['rcountrel'] = 1.0
    for i in range(len(analyzed) // 2):
        if analyzed[2*i + 2]['rcount']:
            analyzed[2*i + 2]['rcountrel'] = round(analyzed[2*i]['rcount'] / analyzed[2*i+2]['rcount'], 3)
        else:
            analyzed[2*i + 2]['rcountrel'] = 100500
    return analyzed

def str_state(state):
    return "<{state},{final},{incount},{outcount},{rcount},{rcountrel}>".format(**state)

THRESHOLD = { 'incount' : 1, 'final' : 0, 'outcount' : 1, 'rcountrel' : 1.0 }

def str_state_key(state, key):
    if not THRESHOLD.get(key) or state[key] > THRESHOLD[key]:
        return " <{0}:{1}> ".format(state['state'], state[key])
    else:
        return ""


with open('sm-min.json', 'r', encoding='utf-8') as f \
   , open("trace.txt", 'w', encoding='utf-8') as trace:
    sm = f.read()
    sm = state_machine.from_json(sm)
    print(sm.to_json(), file=trace)

    inc = incount(sm)
    print(inc, file=trace)

    outc = outcount(sm)
    print(outc, file=trace)

    rc = rcount(sm)
    print(rc, file=trace)

    targets = {}
    for key in KEYS:
        targets[key] = open("metric-" + key + ".txt", "w", encoding='utf-8')
    
    with open("dict.txt", 'r', encoding='utf-8') as words:
        with open('metrics.json', 'w', encoding='utf-8') as metrics \
           , open('metrics.txt', 'w', encoding='utf-8') as metrics_txt:
            for word in words:
                analyzed_word = word_analyzer(sm, word)
                line = ''
                for p in analyzed_word:
                    if type(p) is dict:
                        line += str_state(p)
                    else:
                        line += p
                print(line, file=metrics_txt)

                for key in KEYS:
                    line = ''
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
