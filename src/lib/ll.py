from typing import Dict, Tuple

from graphviz import Digraph

from builder import Builder
from grammar import Grammar, Rule, NTerminal, Terminal, Epsilon


class LL1Parser:
    def __init__(self, builder: Builder):
        self.builder = builder
        self.builder.build_first()
        self.builder.build_follow()
        self.ll1_table = self.build_ll1_table()

    def build_ll1_table(self) -> Dict[Tuple[NTerminal, Terminal], Rule]:
        ll1_table = {}

        if not self.builder.is_ll1():
            raise Exception('Provided grammar is not LL(1)')

        for rule in self.builder.grammar.rules:
            left = rule.left[0]
            first_set = self.builder.get_first(rule.right)

            for symbol in first_set:
                if symbol != Epsilon():
                    ll1_table[(left, symbol)] = rule
                else:
                    follow_set = self.builder.follow[left]
                    for follow_symbol in follow_set:
                        ll1_table[(left, follow_symbol)] = rule

        return ll1_table

    def parse_input(self, input_string: str):
        graph = Digraph(comment='LL1 Tree')
        graph.format = 'png'

        stack = [Terminal('$'), self.builder.grammar.start]
        input_string += '$'
        input_seq = self.builder.grammar.str_to_seq(input_string)
        input_index = 0

        node_stack = [0]
        next_node_id = 1
        graph.node(str(0), self.builder.grammar.start.__str__())
        while stack:
            top_symbol = stack[-1]
            current_input_symbol = input_seq[input_index]

            if isinstance(top_symbol, Terminal) and top_symbol != '$':
                if top_symbol == current_input_symbol:
                    stack.pop()
                    node_stack.pop()

                    input_index += 1
                else:
                    return False
            elif isinstance(top_symbol, NTerminal):
                if (top_symbol, current_input_symbol) in self.ll1_table:
                    rule = self.ll1_table[(top_symbol, current_input_symbol)]
                    stack.pop()

                    par = node_stack.pop()

                    for ci, symbol in enumerate(reversed(rule.right)):
                        if symbol == Epsilon():
                            continue

                        next_node_id += 1
                        node_stack.append(next_node_id)
                        graph.node(str(next_node_id), symbol.__str__())
                        graph.edge(str(par), str(next_node_id))

                        stack.append(symbol)
                else:
                    return False
            elif top_symbol == '$' and current_input_symbol == '$':

                break
            else:
                return False

        if input_index == len(input_seq) - 1:
            graph.render('ll', view=False, directory='src/lib/static/img/')
            return True
        else:
            return False
