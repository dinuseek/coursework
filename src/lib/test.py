from grammar import GrammarReader
from builder import Builder
from earley import EarleyParser

test = '''
{
  "terms": [
    "0",
    "1",
    "+",
    "*",
    "(",
    ")"
  ],
  "nterms": [
    "E",
    "T",
    "F"
  ],
  "rules": [
    "E := E + T",
    "E := T",
    "T := T * F",
    "T := F",
    "F := ( E )",
    "F := 0",
    "F := 1"
  ],
  "start": "E"
}
'''


reader = GrammarReader()
grammar = reader.parse(test)
builder = Builder(grammar)
parser = Ear

builder.eliminate_left_recursion()
for rule in grammar.rules:
    print(rule)

pass
