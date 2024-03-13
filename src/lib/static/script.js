let mode = 'operations';

function apply_operation(op) {
    let request;
    if (op === 0){
        request = '/remove_eps_rules';
    } else if (op === 1){
        request = '/remove_left_recursion';
    } else if (op === 2){
        request = '/remove_right_branching';
    }

    fetch(request, {
        method: 'GET'
    })
        .then(response => response.json())
        .then(data => {
            if (!data['success']) {
                document.getElementById('grammar-errors').textContent = data['error'];
            } else {
                document.getElementById('grammar-errors').textContent = '';
                const outNode = document.getElementById('grammar-out')
                outNode.innerHTML = '';
                for (let i = 0; i < data['result'].length; i++) {
                    let span = document.createElement('span');
                    span.textContent = data['result'][i];
                    outNode.appendChild(span);
                    outNode.appendChild(document.createElement('br'));
                }
            }
        })
        .catch(error => console.error(error));
}

function loadIndex1() {
    fetch('/index1')
        .then(response => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => document.body.innerHTML = data)
        .catch(error => console.error('Error:', error));
}

function loadIndex() {
    fetch('/')
        .then(response => {
            if (response.ok) {
                return response.text();
            }
            throw new Error('Network response was not ok.');
        })
        .then(data => {
            document.body.innerHTML = data;
            mode = 'operations';
        })
        .catch(error => console.error('Error:', error));
}

function changeMode(button) {
    var buttons = document.querySelectorAll('#ll, #lr, #earley');
    buttons.forEach(function (btn) {
        btn.classList.remove('selected');
    });
    button.classList.add('selected');

    mode = button.id;
}

function processGrammar() {
    const text = document.getElementById('input-grammar').value;
    fetch('/process_grammar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({mode: mode, text: text}),
    })
        .then(response => response.json())
        .then(data => {
            if (!data['success']) {
                document.getElementById('grammar-errors').textContent = data['error'];
            } else {
                document.getElementById('grammar-errors').textContent = '';
                const outNode = document.getElementById('grammar-out');
                while (outNode.firstChild) {
                    outNode.firstChild.remove();
                }

                if (mode === 'll') {
                    let table_dict = data['table']
                    let terms = data['terms']
                    let nterms = data['nterms']

                    let table = '<table>';
                    table += '<tr>'
                    table += '<th> </th>'
                    for (let j = 0; j < terms.length; j++) {
                        let term = terms[j];
                        table += '<th>' + term + '</th>'
                    }
                    table += '</tr>'

                    for (let i = 0; i < nterms.length; i++) {
                        let nterm = nterms[i];
                        table += '<tr>';
                        table += '<th>' + nterm + '</th>'
                        for (let j = 0; j < terms.length; j++) {
                            let term = terms[j];
                            if (nterm in table_dict && term in table_dict[nterm]) {
                                table += '<td>' + table_dict[nterm][term] + '</td>'
                            } else {
                                table += '<td> </td>'
                            }
                        }
                        table += '</tr>'
                    }
                    table += '</table>'

                    outNode.innerHTML = table;
                } else if (mode === 'lr') {
                    let sets = data['sets']
                    let sets_el = document.createElement('div');
                    outNode.appendChild(sets_el);

                    for (let i = 0; i < sets.length; i++) {
                        let span = document.createElement('span');
                        span.innerHTML += '<h3>' + i + '</h3>'
                        for (let j = 0; j < sets[i].length; j++) {
                            span.innerHTML += sets[i][j] + '<br>'
                        }
                        sets_el.appendChild(span);
                    }

                    let table_dict = data['table'];
                    let gotos_dict = data['gotos'];
                    let symbols = data['symbols'];
                    let table_el = document.createElement('div');
                    outNode.appendChild(table_el);

                    let table = '<table>';
                    table += '<tr>'
                    table += '<th> </th>'
                    for (let j = 0; j < symbols.length; j++) {
                        let symbol = symbols[j];
                        table += '<th>' + symbol + '</th>'
                    }
                    table += '</tr>'

                    for (let i = 0; i < sets.length; i++) {
                        table += '<tr>';
                        table += '<th>' + i + '</th>'
                        for (let j = 0; j < symbols.length; j++) {
                            let symbol = symbols[j];
                            if (i.toString() in table_dict && symbol in table_dict[i.toString()]) {
                                let t = table_dict[i.toString()][symbol]
                                if (!isNaN(parseInt(t))) {
                                    table += '<td>s(' + table_dict[i.toString()][symbol] + ')</td>'
                                } else {
                                    table += '<td>' + table_dict[i.toString()][symbol] + '</td>'
                                }
                            } else if (i.toString() in gotos_dict && symbol in gotos_dict[i.toString()]) {
                                table += '<td>g(' + gotos_dict[i.toString()][symbol] + ')</td>'
                            } else {
                                table += '<td> </td>'
                            }
                        }
                        table += '</tr>'
                    }

                    table += '</table>'
                    table_el.innerHTML = table;
                } else if (mode === 'earley'){

                }
            }
        })
        .catch(error => console.error(error));
}


function processSeq() {
    const text = document.getElementById('input-seq').value;
    fetch('/process_seq', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({mode: mode, text: text}),
    })
        .then(response => response.json())
        .then(data => {
            if (!data['success']) {
                document.getElementById('seq-errors').textContent = data['error'];
            } else {
                document.getElementById('seq-errors').textContent = '';
                let outNode = document.getElementById('seq-out');
                while (outNode.firstChild) {
                    outNode.firstChild.remove();
                }
                if (mode === 'll') {
                    if (data['result']) {
                        let graph = document.createElement('img');
                        graph.src = '../static/img/ll.png?' + new Date().getTime();
                        outNode.appendChild(graph)
                    } else {
                        outNode.textContent = 'Входная цепочка не может быть разобрана.'
                    }
                } else if (mode === 'lr') {
                    if (data['result']) {
                        let graph = document.createElement('img');
                        graph.src = '../static/img/lr.png?' + new Date().getTime();
                        outNode.appendChild(graph)
                    } else {
                        outNode.textContent = 'Входная цепочка не может быть разобрана данным автоматом.'
                    }
                } else if (mode === 'earley') {
                    if (data['result']){
                        outNode.textContent = 'Цепочка выводится грамматикой.'
                    } else {
                        outNode.textContent = 'Цепочка НЕ выводится грамматикой.'
                    }
                }
            }
        })
        .catch(error => console.error(error));
}