from src.lib.earley import EarleyParser
from src.lib.grammar import GrammarReader
from src.lib.builder import Builder
from src.lib.ll import LL1Parser

reader = GrammarReader()
test = 11
grammar = reader.parse(f'/home/kurikuri/Projects/bmstu/course_work/CFgram/pythonProject/test/grammar/{test}.json')
builder = Builder(grammar)


print()
erley_parser = EarleyParser(builder)
print(erley_parser.parse('n+n'))
erley_parser.build_parse_forest()
erley_parser.view_parse_forest()
pass
