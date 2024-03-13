from typing import List, Set

from graphviz import Digraph

from builder import Builder
from grammar import Rule, Terminal, Epsilon, NTerminal


class Situation:
    def __init__(self, rule: Rule, pos: int, pre: Terminal):
        self.rule = rule
        self.pos = pos
        self.pre = pre

    def __str__(self):
        right = [symbol.__str__() for symbol in self.rule.right]
        right.insert(self.pos, '·')
        return f'{" ".join([symbol.__str__() for symbol in self.rule.left])} := {" ".join(right)} \\\\ {self.pre}'

    def get_next_symbol(self):
        return self.rule.right[self.pos]

    def before(self):
        return self.rule.right[:self.pos]

    def after_pre(self):
        return self.rule.right[self.pos + 1:]

    def is_end(self):
        return self.pos == len(self.rule.right)

    def __eq__(self, other):
        if isinstance(other, Situation):
            return self.rule == other.rule and self.pos == other.pos and self.pre == other.pre
        return False

    def __hash__(self):
        return hash((self.rule, self.pos, self.pre))


class LR1Parser:

    def __init__(self, builder: Builder):
        self.builder = builder
        builder.build_first()
        builder.build_follow()
        self.sets: List[Set[Situation]] = []
        self.T, self.gotos = self.build_table()

    def closure(self, sits: Set[Situation]):
        I = sits.copy()
        J = I.copy()
        changed = True
        while changed:
            I = J.copy()
            J = I.copy()
            changed = False
            for sit in I:
                if sit.is_end():
                    continue
                B = sit.get_next_symbol()
                for rule in self.builder.grammar.rules:
                    if rule.left[0] == B:
                        for b in self.builder.get_first(sit.after_pre()):
                            new_sit = Situation(rule, 0, b if b != Epsilon() else sit.pre)
                            if new_sit not in J:
                                J.add(new_sit)
                                changed = True
        return J

    def goto(self, sits, X):
        J = set()
        for sit in sits:
            if not sit.is_end() and sit.get_next_symbol() == X:
                J.add(Situation(sit.rule, sit.pos + 1, sit.pre))
        return self.closure(J)

    def build(self):
        self.sets = []
        changed = True
        old_start = self.builder.grammar.start
        new_start = self.builder.get_new_nterm(self.builder.grammar.start)
        new_start_rule = Rule((new_start,), (self.builder.grammar.start,))
        self.builder.grammar.rules.append(new_start_rule)
        self.builder.grammar.start = new_start
        self.sets.append(self.closure({Situation(new_start_rule, 0, Terminal('$'))}))
        while changed:
            changed = False
            for sits in self.sets:
                for nterm in self.builder.grammar.nterms + self.builder.grammar.terms:
                    goto = self.goto(sits, nterm)
                    if goto and goto not in self.sets:
                        self.sets.append(goto)
                        changed = True
        # self.builder.grammar.start = old_start

    def build_table(self):
        self.build()
        gotos = {}
        T = {}

        for i in range(len(self.sets)):
            for sit in self.sets[i]:
                if not sit.is_end() and isinstance(sit.get_next_symbol(), Terminal):
                    goto = self.goto(self.sets[i], sit.get_next_symbol())
                    if goto in self.sets:
                        if (i, sit.get_next_symbol()) in gotos.keys():
                            raise Exception('Ambiguity detected')
                        if (i, sit.get_next_symbol()) in T.keys() and \
                                T[(i, sit.get_next_symbol())] != self.sets.index(goto):
                            raise Exception('Ambiguity detected')
                        T[(i, sit.get_next_symbol())] = self.sets.index(goto)
                if sit.is_end():
                    if sit.rule.left[0] != self.builder.grammar.start:
                        if (i, sit.pre) in T.keys():
                            raise Exception('Ambiguity detected')
                        T[(i, sit.pre)] = sit.rule
                if sit.rule.left[0] == self.builder.grammar.start:
                    if sit.is_end():
                        if (i, sit.pre) in T.keys():
                            raise Exception('Ambiguity detected')
                        T[(i, sit.pre)] = True
                for nterm in self.builder.grammar.nterms:
                    goto = self.goto(self.sets[i], nterm)
                    if goto in self.sets:
                        if (i, nterm) in T.keys():
                            raise Exception('Ambiguity detected')
                        if (i, nterm) in gotos.keys() and gotos[(i, nterm)] != self.sets.index(goto):
                            raise Exception('Ambiguity detected')
                        gotos[(i, nterm)] = self.sets.index(goto)

        return T, gotos

    def parse_input(self, input_string: str):
        graph = Digraph(comment='LR1 Tree')
        graph.format = 'png'
        graph.graph_attr['rankdir'] = 'LR'
        node_idx = 0

        stack = [0]
        input_string += '$'
        input_seq = self.builder.grammar.str_to_seq(input_string)
        input_index = 0

        while input_index < len(input_seq):
            cur_state = stack[-1]
            cur_symbol = input_seq[input_index]
            if (cur_state, cur_symbol) in self.T:
                action = self.T[(cur_state, cur_symbol)]
                if action is True:
                    graph.render('lr', view=False, directory='src/lib/static/img/')
                    return True
                elif isinstance(action, int):
                    s = action
                    stack.append(cur_symbol)
                    stack.append(s)
                    input_index += 1
                elif isinstance(action, Rule):
                    seq_tmp = []
                    for c in stack:
                        if isinstance(c, Terminal) or isinstance(c, NTerminal):
                            seq_tmp.append(c)
                    seq_tmp += input_seq[input_index:]
                    graph.node(str(node_idx), ' '.join(list(map(lambda x: str(x), seq_tmp))))

                    for i in range(len(action.right)):
                        stack = stack[:-2]
                    s = stack[-1]
                    stack.append(action.left[0])
                    stack.append(self.gotos[(s, action.left[0])])

                    seq_tmp = []
                    for c in stack:
                        if isinstance(c, Terminal) or isinstance(c, NTerminal):
                            seq_tmp.append(c)
                    seq_tmp += input_seq[input_index:]
                    graph.node(str(node_idx + 1), ' '.join(list(map(lambda x: str(x), seq_tmp))))
                    graph.edge(str(node_idx), str(node_idx + 1), label=str(action))
                    node_idx += 1
                else:
                    return False
            else:
                return False
