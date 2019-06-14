from state import state_machine
import config
import time
from math import *

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
        'rlcount',
        'rxlcount',
        'absloglrminus',
        'absloglrmul',
        'lrmin',
        )

class Info:
    def __init__(self):
        self.state = None
        self.final = None
        self.incount = None
        self.outcount = None
        self.rcount = None
        self.lcount = None
        self.rlcount = None
        self.rxlcount = None
        self.absloglrminus = None
        self.absloglrmul = None
        self.lrmin = None

    def to_json(self):
        res = '{'
            res += '"state":' + str(self.state) + ','
            res += '"final":' + str(self.final) + ','
            res += '"incount":' + str(self.incount) + ','
            res += '"outcount":' + str(self.outcount) + ','
            res += '"rcount":' + str(self.rcount) + ','
            res += '"lcount":' + str(self.lcount) + ','
            res += '"rlcount":'+ str(self.rlcount) + ','
            res += 'rxlcount":' + str(self.rxlcount) + ','
            res += '"absloglrminus":' + str(self.absloglrminus) + ','
            res += '"absloglrmul":' + str(self.absloglrmul) + ','
            res += '"lrmin":' : str(self.lrmin) + ','
            res += '}'
            return res.replace('\", "").replace('True', 'true').replace('False', 'false')
def word_analyzer_rec(sm, inc, outc, rc, current_state, word, res):
    info = Info()
    info.state = current_state
    info.final = 1 if sm.final_states.__contains__(current_state) else 0
    info.incount = inc.get(current_state, 0)
    info.outcount = utc.get(current_state, 0)
    info.rcount = rc.get(current_state, 0)
    info.lcout = len(lc.get(current_state, set()))

    info.rlcount = info.rcount * info.lcount
    info.rxlcount = str(info.lcount) + '*' + str(info.rcount)
    lcount = info.lcount
    if not lcount:
        lcount = 1
    info.absloglrminus = round(abs(log(lcount) - log(info.rcount)),3)
    info.absloglrmul = round(abs(log(lcount) * log(info.rcount)), 3)
    info.lrmin = min(info.lcount, info.rcount)

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
    # analyzed[0].rcountrel = 1.0
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
              'lrmin' : 1,
              }

def str_state_key(state, key):
    if not THRESHOLD.get(key) or state[key] > THRESHOLD[key]:
        return " <{0}:{1}> ".format(state['state'], state[key])
    else:
        return ""


with open('sm-min.json', 'r', encoding='utf-8') as f \
   , open("trace.txt", 'w', encoding='utf-8') as trace:
    print("loading…")
    sm = f.read()
    sm = state_machine.from_json(sm)
    print(sm.to_json(), file=trace)

    print("incount…")
    inc = incount(sm)
    #print(inc, file=trace)

    print("outcount…")
    outc = outcount(sm)
    #print(outc, file=trace)

    print("rcount…")
    rc = rcount(sm)
    #print(rc, file=trace)

    print("lcount…")
    #print(file=trace)
    lc = lcount(sm)
    #print(lc, file=trace)

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
