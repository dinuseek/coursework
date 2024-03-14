from typing import Dict, Set
from copy import deepcopy

from grammar import *
from utils import is_context_free
from trie import Trie


class Builder:
    first: Dict[NTerminal, Set] = {}
    follow = {}

    def get_new_nterm(self, nterm: NTerminal):
        new_nterm = NTerminal(nterm.symbol)
        while new_nterm in self.grammar.nterms:
            new_nterm.symbol += "'"
        return new_nterm

    def get_first(self, seq: List[Union[Union[NTerminal, Terminal], Epsilon]]):
        first = set()
        for symbol in seq:
            if isinstance(symbol, Terminal) or isinstance(symbol, Epsilon):
                first.add(symbol)
                break
            else:
                first |= self.first[symbol] - {Epsilon()}
                if Epsilon() not in self.first[symbol]:
                    break
        else:
            first.add(Epsilon())

        return first

    def build_first(self):
        for nterm in self.grammar.nterms:
            self.first[nterm] = set()

        changed = True
        while changed:
            changed = False
            for rule in self.grammar.rules:
                left = rule.left[0]
                first_ = self.get_first(rule.right)
                if first_ - self.first[left]:
                    self.first[left] |= first_
                    changed = True

    def build_follow(self):
        for nterm in self.grammar.nterms:
            self.follow[nterm] = set()
        self.follow[self.grammar.start].add(Terminal('$'))

        changed = True
        while changed:
            changed = False
            for rule in self.grammar.rules:
                left = rule.left[0]
                for i, symbol in enumerate(rule.right):
                    if not isinstance(symbol, NTerminal):
                        continue

                    first_ = self.get_first(rule.right[i + 1:])
                    if first_ - {Epsilon()} - self.follow[symbol]:
                        self.follow[symbol] |= first_ - {Epsilon()}
                        changed = True

                    if Epsilon() in first_:
                        if self.follow[left] - self.follow[symbol]:
                            self.follow[symbol] |= self.follow[left]

    def get_epsilon_gens(self):
        epsilone_gens = set()
        for rule in self.grammar.rules:
            if len(rule.right) == 1 and rule.right[0] == Epsilon():
                epsilone_gens.add(rule.left[0])

        changed = True
        while changed:
            changed = False
            for rule in self.grammar.rules:
                for symbol in rule.right:
                    if not isinstance(symbol, NTerminal) or symbol not in epsilone_gens:
                        break
                else:
                    if rule.left[0] not in epsilone_gens:
                        epsilone_gens.add(rule.left[0])
                        changed = True
        return epsilone_gens

    def eliminate_epsilon_rules(self):
        epsilon_gens = self.get_epsilon_gens()

        new_rules = []
        for rule in self.grammar.rules:
            epsilon_combinations = [[]]
            for symbol in rule.right:
                if symbol in epsilon_gens:
                    new_combinations = []
                    for combination in epsilon_combinations:
                        new_combinations.append(combination + [symbol])
                        new_combinations.append(combination)
                    epsilon_combinations = new_combinations
                else:
                    epsilon_combinations = [combination + [symbol] for combination in epsilon_combinations]

            for combination in epsilon_combinations:
                if len(combination) == 0:
                    combination.append(Epsilon())
                new_rules.append(Rule(rule.left, combination))

        new_rules_ = []
        for rule in new_rules:
            if len(rule.right) == 1 and rule.right[0] == Epsilon():
                if rule.left[0] == self.grammar.start:
                    new_start = self.get_new_nterm(self.grammar.start)
                    self.grammar.nterms.append(new_start)
                    new_rules_.append(Rule([new_start], [self.grammar.start]))
                    new_rules_.append(Rule([new_start], [Epsilon()]))
                    self.grammar.start = new_start
                continue
            new_rules_.append(rule)

        self.grammar.rules = new_rules_.copy()

    def eliminate_left_recursion(self):
        new_nterms = []
        rules = self.grammar.rules.copy()
        for i, nterm1 in enumerate(self.grammar.nterms):
            for j in range(i):
                nterm2 = self.grammar.nterms[j]
                new_rules = []
                for rule in rules:
                    if rule.left[0] == nterm1:
                        if rule.right[0] == nterm2:
                            for rule2 in rules:
                                if rule2.left[0] == nterm2:
                                    new_rules.append(Rule((nterm1,), rule2.right + rule.right[1:]))
                            continue
                    new_rules.append(rule)
                rules = new_rules

            to_eliminate = False
            for rule in rules:
                if rule.left[0] == nterm1:
                    if rule.right[0] == nterm1:
                        to_eliminate = True
            if to_eliminate:
                new_nterm = self.get_new_nterm(nterm1)
                new_nterms.append(new_nterm)
                new_rules = []
                for rule in rules:
                    if rule.left[0] == nterm1:
                        if rule.right[0] == nterm1:
                            new_rules.append(Rule((new_nterm,), rule.right[1:] + (new_nterm,)))
                            new_rules.append(Rule((new_nterm,), rule.right[1:]))
                        else:
                            new_rules.append(Rule((nterm1,), rule.right + (new_nterm,)))
                            new_rules.append(rule)
                    else:
                        new_rules.append(rule)

                rules = new_rules.copy()

        self.grammar.nterms += new_nterms
        self.grammar.rules = rules

    def eliminate_right_branching(self):
        new_rules_ = deepcopy(self.grammar.rules)

        change = True
        while change:
            change = False
            rules_cum = []
            for nterm in self.grammar.nterms:
                rules = [rule for rule in new_rules_ if rule.left[0] == nterm]
                common_prefix = self.find_common_prefix(rules)
                while common_prefix:
                    change = True
                    new_rules = []
                    if common_prefix:
                        new_nterm = self.get_new_nterm(nterm)
                        self.grammar.nterms.append(new_nterm)
                        for rule in rules:
                            if rule.left[0] == nterm and list(rule.right[:len(common_prefix)]) == common_prefix:
                                new_rule_1 = Rule((nterm,), common_prefix + [new_nterm])
                                if new_rule_1 not in new_rules:
                                    new_rules.append(new_rule_1)
                                new_rule_2 = Rule((new_nterm,), rule.right[len(common_prefix):])
                                if not len(new_rule_2.right):
                                    new_rule_2.right += (Epsilon(),)
                                if new_rule_2 not in new_rules:
                                    new_rules += (new_rule_2,)
                            else:
                                if rule not in new_rules:
                                    new_rules += (rule,)

                    rules = new_rules

                    common_prefix = self.find_common_prefix([rule for rule in rules if rule.left[0] == nterm])
                rules_cum += rules
            new_rules_ = rules_cum

        self.grammar.rules = new_rules_

    def find_common_prefix(self, rules):
        trie = Trie()
        for rule in rules:
            trie.insert(rule.right)
        return trie.find_best_prefix()

    def is_ll1(self):
        for nterm in self.grammar.nterms:
            rules = [rule for rule in self.grammar.rules if rule.left[0] == nterm]
            firsts = [self.get_first(rule.right) for rule in rules]
            for i in range(len(rules)):
                for j in range(len(rules)):
                    if i == j:
                        continue
                    if firsts[i].intersection(firsts[j]):
                        return False
                    if Epsilon() in firsts[i] and self.follow[nterm].intersection(firsts[j]):
                        return False
        return True

    def __init__(self, grammar: Grammar):
        if not is_context_free(grammar):
            raise Exception('Provided grammar is not CF')
        self.grammar = grammar
