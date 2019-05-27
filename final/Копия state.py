import json
import io

class state:
    next_id = 0
    
    def __init__(self):
        self.id = state.next_id
        self.gotos = {}
        self.final = False
        state.next_id += 1
    
    def to_map(self):
        obj = {'final': self.final}
        m = dict(self.gotos)
        for k in m:
            m[k] = m[k].to_map()
        obj['gotos'] = m
        return obj
    
    def to_json(self):
        return str(self.to_map()).replace('\'', '\"').replace('False', 'false').replace('True', 'true')
    
    @staticmethod
    def from_map(m):
        s = state()
        s.final = m['final']
        for k in m['gotos']:
            s.gotos[k] = state.from_map(m['gotos'][k])
        return s
    
    @staticmethod
    def from_json(s):
        return state.from_map(json.loads(s))

    def get_final_states(self):
        res = set()
        if self.final:
            res.add(self.id)
        for k in self.gotos:
            res.update(self.gotos[k].get_final_states())
        return res

    def get_states(self):
        res = set()
        res.add(self.id)
        for k in self.gotos:
            res.update(self.gotos[k].get_states())
        return res

    def get_transitions(self, res={}):
        for k in self.gotos:
            res.setdefault(self.id, {}).setdefault(k, set()).add(self.gotos[k].id)
            self.gotos[k].get_transitions(res)
        return res


class state_machine:
    def __init__(self):
        self.states = set()
        self.start_states = set()
        self.final_states = set()
        self.transitions = {}
        self.alphabet = ''

    @staticmethod
    def from_tree(start, alphabet):
        sm = state_machine()
        sm.alphabet = alphabet
        sm.start_states = {start.id}
        sm.final_states = start.get_final_states()
        sm.states = start.get_states()
        sm.transitions = start.get_transitions()
        return sm

    def to_map(self):
        return {
            'alphabet': self.alphabet,
            'start_states': list(self.start_states),
            'final_states': list(self.final_states),
            'states': list(self.states),
            'transitions': {str(state_id): {letter: list(states) for letter, states in trans.items() } for state_id, trans in self.transitions.items()}
        }

    def to_json(self):
        return str(self.to_map()).replace('\'', '\"')

    @staticmethod
    def from_map(m):
        sm = state_machine()
        sm.alphabet = m['alphabet']
        sm.start_states = set(m['start_states'])
        sm.final_states = set(m['final_states'])
        sm.states = set(m['states'])
        sm.transitions = {int(state_id): {letter: set(states) for letter, states in trans.items() } for state_id, trans in m['transitions'].items()}
        return sm

    @staticmethod
    def from_json(s):
        return state_machine.from_map(json.loads(s))


    
