from flask import Flask, render_template, request, jsonify

from builder import Builder
from grammar import GrammarReader
from src.lib.earley import EarleyParser
from src.lib.ll import LL1Parser
from src.lib.lr import LR1Parser
from text_to_json import convert_text_to_json

app = Flask(__name__)
grammar = None
builder = None
ll1_parser = None
lr1_parser = None
earley_parser = None
input_seq = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/index1')
def index1():
    return render_template('index1.html')


@app.route('/remove_eps_rules', methods=['GET'])
def delete_epsilon_rules():
    global grammar
    global builder
    if grammar is None:
        return jsonify({'success': False,
                        'error': 'Введите грамматику!'})
    builder.eliminate_epsilon_rules()
    out = [str(rule) for rule in builder.grammar.rules]
    return jsonify({'success': True,
                    'result': out})


@app.route('/remove_left_recursion', methods=['GET'])
def delete_left_recursion():
    global grammar
    global builder
    if grammar is None:
        return jsonify({'success': False,
                        'error': 'Введите грамматику!'})
    builder.eliminate_left_recursion()
    out = [str(rule) for rule in builder.grammar.rules]
    return jsonify({'success': True,
                    'result': out})


@app.route('/remove_right_branching', methods=['GET'])
def delete_right_branching():
    global grammar
    global builder
    if grammar is None:
        return jsonify({'success': False,
                        'error': 'Введите грамматику!'})
    builder.eliminate_right_branching()
    out = [str(rule) for rule in builder.grammar.rules]
    return jsonify({'success': True,
                    'result': out})


@app.route('/process_grammar', methods=['POST'])
def process_grammar():
    global grammar
    global builder
    global ll1_parser
    global lr1_parser
    global earley_parser

    data = request.get_json()
    text = str(data.get('text'))
    reader = GrammarReader()
    try:
        grammar = reader.parse(convert_text_to_json(text))
        builder = Builder(grammar)
    except Exception as e:
        return jsonify({'success': False,
                        'error': str(e)})

    mode = str(data.get('mode'))
    if mode == 'operations':
        return jsonify({'success': True})
    elif mode == 'll':
        try:
            ll1_parser = LL1Parser(builder)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})

        table_dict = ll1_parser.ll1_table

        table = {}
        for k, v in table_dict.items():
            col = table.get(str(k[0]), dict())
            col[str(k[1])] = str(v)
            table[str(k[0])] = col

        return jsonify({'success': True,
                        'table': table,
                        'terms': list(map(lambda x: str(x), builder.grammar.terms)),
                        'nterms': list(map(lambda x: str(x), builder.grammar.nterms))})
    elif mode == 'lr':
        try:
            lr1_parser = LR1Parser(builder)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})
        T_dict, gotos_dict = lr1_parser.T, lr1_parser.gotos

        sets = []
        for set in lr1_parser.sets:
            sets.append([str(el) for el in set])

        T = {}
        for k, v in T_dict.items():
            col = T.get(str(k[0]), dict())
            col[str(k[1])] = str(v)
            T[str(k[0])] = col

        gotos = {}
        for k, v in gotos_dict.items():
            col = gotos.get(str(k[0]), dict())
            col[str(k[1])] = str(v)
            gotos[str(k[0])] = col

        return jsonify({'success': True,
                        'sets': sets,
                        'table': T,
                        'gotos': gotos,
                        'symbols': list(map(lambda x: str(x), builder.grammar.nterms)) + list(
                            map(lambda x: str(x), builder.grammar.terms))})
    elif mode == 'earley':
        try:
            earley_parser = EarleyParser(builder)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})
        return {'success': True}



@app.route('/process_seq', methods=['POST'])
def process_seq():
    global grammar
    global builder
    global ll1_parser
    global lr1_parser
    global earley_parser

    if grammar is None or builder is None:
        return jsonify({'success': False,
                        'error': 'Введите грамматику!'})

    data = request.get_json()
    seq = str(data.get('text'))
    mode = str(data.get('mode'))

    if mode == 'll':
        if ll1_parser is None:
            return jsonify({'success': False,
                            'error': 'Сначала постройте LL1-таблицу'})
        try:
            result = ll1_parser.parse_input(seq)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})
        return jsonify({'success': True,
                        'result': result,
                        'path': 'src/lib/img/ll.png'})
    elif mode == 'lr':
        if lr1_parser is None:
            return jsonify({'success': False,
                            'error': 'Сначала постройте LR1-автомат'})
        try:
            result = lr1_parser.parse_input(seq)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})
        return jsonify({'success': True,
                        'result': result,
                        'path': 'src/lib/img/lr.png'})
    elif mode == 'earley':
        if earley_parser is None:
            return jsonify({'success': False,
                            'error': 'Введите грамматику'})
        try:
            result = earley_parser.parse_input(seq)
        except Exception as e:
            return jsonify({'success': False,
                            'error': str(e)})
        return jsonify({'success': True,
                        'result': result})


if __name__ == '__main__':
    app.run(debug=True)
