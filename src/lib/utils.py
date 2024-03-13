from grammar import NTerminal, Grammar


def is_context_free(grammar: Grammar):
    for rule in grammar.rules:
        if len(rule.left) > 1 or not isinstance(rule.left[0], NTerminal):
            return False
    return True

