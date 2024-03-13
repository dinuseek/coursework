import json


def convert_text_to_json(text):
    lines = text.split('\n')
    terms = []
    nterms = []
    rules = []
    start_symbol = None

    for line in lines:
        parts = line.strip().split(':=', 1)
        if len(parts) < 2:
            continue
        left_part = parts[0].strip()
        right_part = parts[1].strip()

        if start_symbol is None:
            start_symbol = left_part

        if left_part not in nterms:
            nterms.append(left_part)

        for symbol in right_part.split():
            if symbol.isupper():
                if symbol not in nterms:
                    nterms.append(symbol)

        for symbol in right_part.split():
            if symbol not in nterms:
                terms.append(symbol)

        if '.' in terms:
            terms.remove('.')

        rules.append(line.strip())

    json_data = {
        "terms": list(terms),
        "nterms": list(nterms),
        "rules": rules,
        "start": start_symbol
    }

    return json.dumps(json_data, indent=2)


# text = """
#     E := T E'
#     E' := + T E'
#     E' := .
#     T := F T'
#     T' := * F T'
#     T' := .
#     F := n
#     F := ( E )
# """
#
# json_output = convert_text_to_json(text)
# print(json_output)

# E := T E'
# E' := + T E'
# E' := .
# T := F T'
# T' := * F T'
# T' := .
# F := n
# F := ( E )

# E := E + T
# E := T
# T := T * F
# T := F
# F := ( E )
# F := 0
# F := 1