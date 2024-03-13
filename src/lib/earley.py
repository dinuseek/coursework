from typing import List, Set

from graphviz import Digraph

from builder import Builder
from grammar import Rule, NTerminal, Terminal


class Situation:
    def __init__(self, rule: Rule, pos: int, i: int):
        self.rule = rule
        self.pos = pos
        self.i = i

    def __str__(self):
        right = [symbol.__str__() for symbol in self.rule.right]
        right.insert(self.pos, '*')
        return f'{" ".join([symbol.__str__() for symbol in self.rule.left])} -> {" ".join(right)} | {self.i}'

    def get_next_symbol(self):
        return self.rule.right[self.pos]

    def is_end(self):
        return self.pos == len(self.rule.right)

    def __eq__(self, other):
        if isinstance(other, Situation):
            return self.rule == other.rule and self.pos == other.pos and self.i == other.i
        return False

    def __hash__(self):
        return hash((self.rule, self.pos, self.i))


class EarleyParser:
    def __init__(self, builder: Builder):
        self.sits = None
        self.builder = builder
        new_start = self.builder.get_new_nterm(self.builder.grammar.start)
        self.start_rule = Rule((new_start,), (self.builder.grammar.start,))
        self.builder.grammar.rules.append(self.start_rule)
        self.builder.grammar.start = new_start

    def parse_input(self, input_string):
        self.sits: List[Set[Situation]] = []

        input_seq = self.builder.grammar.str_to_seq(input_string)

        start_sit = Situation(self.start_rule, 0, 0)
        self.sits.append({start_sit})

        for i in range(1, len(input_seq) + 1):
            self.sits.append(set())
        for j in range(len(input_seq) + 1):
            self.scan(j, input_seq)

            changed = True
            while changed:
                changed = self.complete(j) or self.predict(j)

        end_sit = Situation(self.start_rule, len(self.start_rule.right), 0)
        if end_sit in self.sits[len(input_seq)]:
            return True
        else:
            return False

    def scan(self, j, seq):
        if j == 0:
            return
        for sit in self.sits[j - 1]:
            if not sit.is_end() and isinstance(sit.get_next_symbol(), Terminal):
                if sit.get_next_symbol() == seq[j - 1]:
                    self.sits[j].add(Situation(sit.rule, sit.pos + 1, sit.i))

    def complete(self, j):
        changed = False
        to_add = set()
        for sit1 in self.sits[j]:
            if sit1.is_end():
                for sit2 in self.sits[sit1.i]:
                    if not sit2.is_end() and isinstance(sit2.get_next_symbol(), NTerminal):
                        new_sit = Situation(sit2.rule, sit2.pos + 1, sit2.i)
                        if new_sit not in self.sits[j]:
                            to_add.add(new_sit)
                            changed = True
        self.sits[j] |= to_add
        return changed

    def predict(self, j):
        changed = False
        to_add = set()
        for sit in self.sits[j]:
            if not sit.is_end() and isinstance(sit.get_next_symbol(), NTerminal):
                for rule in self.builder.grammar.rules:
                    if rule.left[0] == sit.get_next_symbol():
                        new_sit = Situation(rule, 0, j)
                        if new_sit not in self.sits[j]:
                            to_add.add(new_sit)
                            changed = True
        self.sits[j] |= to_add
        return changed
