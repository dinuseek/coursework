import re
from typing import List, Union, Tuple
import json


class Terminal:
    def __init__(self, s: str):
        self.name = s

    def __eq__(self, other):
        if type(other) is str:
            return self.name == other
        elif type(other) is Terminal:
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name


class NTerminal:
    def __init__(self, s: str):
        self.symbol = s

    def __eq__(self, other):
        if type(other) is str:
            return self.symbol == other
        elif type(other) is NTerminal:
            return self.symbol == other.symbol
        else:
            False

    def __hash__(self):
        return self.symbol.__hash__()

    def __str__(self):
        return self.symbol.__str__()


class Epsilon:
    def __str__(self):
        return '.'

    def __eq__(self, other):
        return type(other) is Epsilon

    def __hash__(self):
        return '.'.__hash__()


class Rule:
    def __init__(self, left: Tuple[Union[NTerminal, Terminal]],
                 right: Tuple[Union[Union[NTerminal, Terminal], Epsilon]]):
        self.left: Tuple = tuple(left)
        self.right: Tuple = tuple(right)

    def __eq__(self, other):
        if isinstance(other, Rule):
            return self.left == other.left and self.right == other.right
        return False

    def __str__(self):
        return f'{" ".join([symbol.__str__() for symbol in self.left])} := {" ".join([symbol.__str__() for symbol in self.right])}'

    def __hash__(self):
        return hash((self.left, self.right))


class Grammar:
    def __init__(self, terms: List[Terminal], nterms: List[NTerminal], rules: List[Rule], start: NTerminal):
        self.terms = terms
        self.nterms = nterms
        self.rules = rules
        self.start = start

    def __eq__(self, other):
        if isinstance(other, Grammar):
            return self.terms == other.terms and self.nterms == other and self.rules == other.rules and self.start == other.start

    def str_to_seq(self, s: str) -> List[Union[Terminal, NTerminal]]:
        seq = []
        for symbol in s.split(' '):
            if symbol in self.terms:
                seq.append(Terminal(symbol))
            elif symbol in self.nterms:
                seq.append(NTerminal(symbol))
            else:
                raise Exception('Invalid sequence')
        return seq


class GrammarReader:
    rule_pattern = r'^.+ := .+$'
    terms = []
    nterms = []
    rules = []
    start = None

    def __init__(self):
        self.terms = []
        self.nterms = []
        self.rules = []
        self.start = None

    @staticmethod
    def only_letters(alphabet):
        for word in alphabet:
            if not word.isalpha():
                return False
        return True

    @staticmethod
    def intersects(terms, nterms):
        for term in terms:
            if term in nterms:
                return True
        return False

    def makeTerms(self, terms):
        for term in terms:
            self.terms.append(Terminal(term))
        end_term = Terminal('$')
        if end_term not in self.terms:
            self.terms.append(end_term)

    def makeNTerms(self, nterms):
        for nterm in nterms:
            self.nterms.append(NTerminal(nterm))

    def makeRules(self, rules: List[str]):
        for rule in rules:
            if re.match(self.rule_pattern, rule):
                left = rule.split(':=')[0].strip()
                right = rule.split(':=')[1].strip()

                left_ = []
                right_ = []
                for part, part_ in ((left, left_), (right, right_)):
                    for symbol in part.split(' '):
                        if symbol in self.terms:
                            part_.append(Terminal(symbol))
                        elif symbol in self.nterms:
                            part_.append(NTerminal(symbol))
                        elif symbol == '.':
                            part_.append(Epsilon())
                        else:
                            raise Exception('Unresolved symbol')
                self.rules.append(Rule(left_, right_))
            else:
                raise Exception(f'Invalid rule: {rule}')

    def parse(self, input):
        data = json.loads(input.strip())

        terms = data['terms']
        nterms = data['nterms']
        rules = data['rules']
        start = data['start']

        if self.intersects(terms, nterms):
            raise Exception('There are intersections in the alphabets')
        self.makeTerms(terms)
        self.makeNTerms(nterms)
        self.makeRules(rules)

        if start in nterms:
            self.start = NTerminal(start)

        return Grammar(self.terms, self.nterms, self.rules, self.start)
