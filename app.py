from flask import Flask, request, render_template, redirect, url_for, jsonify
from collections import defaultdict, deque

app = Flask(__name__)

#Variavéis globais
automaton = {}
dfa = None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/input_automaton')
def input_automaton():
    return render_template('input_automaton.html')

@app.route("/save_automaton", methods=["POST"])
def save_automaton():
    global automaton, dfa
    automaton["type"] = request.form["automaton_type"]
    automaton["alphabet"] = request.form["alphabet"].split(",")
    automaton["states"] = request.form["states"].split(",")
    automaton["initial_state"] = request.form["initial_state"]
    automaton["final_states"] = request.form["final_states"].split(",")
    transitions = request.form["transitions"].strip().split("\n")
    automaton["transitions"] = [t.split(",") for t in transitions]

    if automaton["type"] == "AFD":
        if not is_dfa(automaton):
            return render_template("error.html", message="O autômato não é um AFD válido. Verifique as transições para garantir que não haja mais de uma transição para o mesmo símbolo em um estado específico.", automaton=automaton)
        dfa = automaton
    else:
        dfa = None

    return redirect(url_for("automaton_actions"))

@app.route("/automaton_actions")
def automaton_actions():
    global dfa, automaton
    if automaton["type"] == "AFD":
        return redirect(url_for("input_word"))
    return render_template("automaton_actions.html")

@app.route("/convert_to_dfa")
def convert_to_dfa():
    global dfa
    if dfa is None:
        dfa = convert_nfa_to_dfa(automaton)
    return render_template("dfa_result.html", dfa=dfa, show_table=True, is_dfa=is_dfa)


@app.route("/input_word")
def input_word():
    return render_template("input_word.html", dfa=automaton if dfa is None else dfa)

@app.route("/process_word", methods=["POST"])
def process_word():
    global dfa
    word = request.json["word"]
    if dfa is None:
        return jsonify({"error": "DFA not yet converted"}), 500
    
    result, process = simulate_dfa(dfa, word)
    return jsonify({"result": result, "process": process})

@app.route("/reset_automaton")
def reset_automaton():
    global automaton, dfa
    automaton.clear()
    dfa = None
    return redirect(url_for("input_automaton"))


def is_dfa(automaton):
    transitions_map = defaultdict(dict)
    for transition in automaton["transitions"]:
        src, symbol, dest = transition
        if symbol in transitions_map[src]:
            return False
        transitions_map[src][symbol] = dest
    return True

def simulate_dfa(dfa, word):
    current_state = dfa["initial_state"]
    process = []

    for letter in word:
        found_transition = False
        for transition in dfa["transitions"]:
            if (
                transition[0].strip() == current_state
                and transition[1].strip() == letter
            ):
                process.append((current_state, letter, transition[2]))
                current_state = transition[2].strip()
                found_transition = True
                break
        if not found_transition:
            return False, process

    return current_state in dfa["final_states"], process

def convert_nfa_to_dfa(automaton):
    alphabet = automaton['alphabet']
    nfa_transitions = defaultdict(lambda: defaultdict(set))
    
    for transition in automaton['transitions']:
        nfa_transitions[transition[0].strip()][transition[1].strip()].add(transition[2].strip())
    
    start_state = frozenset([automaton['initial_state']])
    dfa_states = set()
    dfa_transitions = {}
    queue = deque([start_state])
    state_name_map = {start_state: 'q0'}
    state_counter = 1
    final_states = set()
    
    while queue:
        current_state = queue.popleft()
        if current_state in dfa_states:
            continue
        
        dfa_states.add(current_state)
        if any(state in automaton['final_states'] for state in current_state):
            final_states.add(state_name_map[current_state])
        
        for symbol in alphabet:
            next_state = frozenset(
                state for nfa_state in current_state for state in nfa_transitions[nfa_state][symbol]
            )
            if next_state:
                if next_state not in state_name_map:
                    state_name_map[next_state] = f'q{state_counter}'
                    state_counter += 1
                    queue.append(next_state)
                dfa_transitions[(state_name_map[current_state], symbol)] = state_name_map[next_state]
    
    return {
        'alphabet': alphabet,
        'states': list(state_name_map.values()),
        'initial_state': state_name_map[start_state],
        'final_states': list(final_states),
        'transitions': [(k[0], k[1], v) for k, v in dfa_transitions.items()]
    }

# def nfa_accepts_word(nfa, word):
#     """Verifica se o NFA aceita a palavra dada."""
#     current_states = set([nfa["initial_state"]])
    
#     for symbol in word:
#         next_states = set()
#         for state in current_states:
#             next_states.update(nfa_transitions(state, symbol, nfa))
#         current_states = next_states
    
#      Verifica se algum estado alcançado é final
#     return any(state in nfa["final_states"] for state in current_states)

def nfa_transitions(state, symbol, nfa):
    """Retorna os estados alcançáveis por transição no AFN."""
    return {trans[2] for trans in nfa["transitions"] if trans[0] == state and trans[1] == symbol}

# Minimização
@app.route("/minimize_dfa")
def minimize_dfa_view():
    global dfa

    minimized_dfa = minimize_dfa(dfa)
    
    return render_template("dfa_minimized.html", dfa=minimized_dfa)


def minimize_dfa(dfa):    
    alphabet = dfa['alphabet']
    states = dfa['states']
    initial_state = dfa['initial_state']
    final_states = set(dfa['final_states'])
    transitions = dfa['transitions']

    equivalence_table = defaultdict(lambda: defaultdict(lambda: False))

    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            state1, state2 = states[i], states[j]
            if (state1 in final_states) != (state2 in final_states):
                equivalence_table[state1][state2] = True

    # Propagar a não-equivalência
    changed = True
    while changed:
        changed = False
        for i in range(len(states)):
            for j in range(i + 1, len(states)):
                state1, state2 = states[i], states[j]
                if equivalence_table[state1][state2]:
                    continue
                for symbol in alphabet:
                    next_state1, next_state2 = None, None
                    for trans in transitions:
                        if trans[0] == state1 and trans[1] == symbol:
                            next_state1 = trans[2]
                        if trans[0] == state2 and trans[1] == symbol:
                            next_state2 = trans[2]
                    if next_state1 and next_state2 and next_state1 != next_state2:
                        if next_state1 > next_state2:
                            next_state1, next_state2 = next_state2, next_state1
                        if equivalence_table[next_state1][next_state2]:
                            equivalence_table[state1][state2] = True
                            changed = True
                            break

    # Agrupar estados equivalentes
    equivalence_classes = {}
    state_to_class = {}
    for state in states:
        for class_state in equivalence_classes:
            if not equivalence_table[min(state, class_state)][max(state, class_state)]:
                equivalence_classes[class_state].add(state)
                state_to_class[state] = class_state
                break
        else:
            equivalence_classes[state] = {state}
            state_to_class[state] = state

    # Construir o DFA minimizado
    minimized_states = list(equivalence_classes.keys())
    minimized_transitions = []
    minimized_final_states = {state_to_class[state] for state in final_states}

    added_transitions = set()
    for class_state, class_group in equivalence_classes.items():
        for symbol in alphabet:
            for state in class_group:
                for trans in transitions:
                    if trans[0] == state and trans[1] == symbol:
                        next_state = trans[2]
                        trans_tuple = (class_state, symbol, state_to_class[next_state])
                        if trans_tuple not in added_transitions:
                            minimized_transitions.append(trans_tuple)
                            added_transitions.add(trans_tuple)
                        break

    minimized_initial_state = state_to_class[initial_state]

    # Identificar estados alcançáveis
    reachable_states = set()
    to_process = [minimized_initial_state]
    while to_process:
        current = to_process.pop()
        if current not in reachable_states:
            reachable_states.add(current)
            for trans in minimized_transitions:
                if trans[0] == current:
                    to_process.append(trans[2])

    minimized_transitions = [trans for trans in minimized_transitions if trans[0] in reachable_states]
    minimized_states = [state for state in minimized_states if state in reachable_states]
    minimized_final_states = [state for state in minimized_final_states if state in reachable_states]

    if len(minimized_states) == len(states) and len(minimized_transitions) == len(transitions):
        return None  

    return {
        'alphabet': alphabet,
        'states': minimized_states,
        'initial_state': minimized_initial_state,
        'final_states': list(minimized_final_states),
        'transitions': minimized_transitions
    }


@app.route("/input_word_afn")
def input_word_afn():
    return render_template("input_word_afn.html", afn=automaton)

@app.route("/get_automaton")
def get_automaton():
    global automaton  
    return jsonify(automaton)

@app.route("/process_afn_word", methods=['POST'])
def process_afn_word():
    data = request.get_json()

    if 'automaton' in data and 'word' in data:
        automaton_data = data['automaton']
        word = data['word']

        print(f"Recebido automato: {automaton_data}")
        print(f"Palavra a ser processada: {word}")

        result, process = simulate_afn(automaton_data, word)

        if result is not None and process is not None:
            response = {
                'result': result,
                'process': process
            }
            print(f"Resposta enviada: {response}")  
            return jsonify(response)
        else:
            error_message = {'error': 'Erro ao simular AFN'}
            print(f"Erro ao simular AFN: {error_message}")  
            return jsonify(error_message), 500
    else:
        error_message = {'error': 'Dados incompletos'}
        print(f"Dados incompletos: {error_message}")
        return jsonify(error_message), 400


def simulate_afn(automaton_data, word):
    state = automaton_data["initial_state"]
    process = []

    current_states = epsilon_closure(automaton_data, [state])
    print(f"Estados iniciais: {current_states}")

    for letter in word:
        next_states = set()
        for current_state in current_states:
 
            for transition in automaton_data["transitions"]:
                src, symbol, dest = transition
                src = src.strip()
                symbol = symbol.strip()
                dest = dest.strip()

                if src == current_state and symbol == letter:
                    next_states.update(epsilon_closure(automaton_data, [dest]))
                    print(f"Transição: {current_state} --({letter})--> {dest}, Fecho-épsilon: {epsilon_closure(automaton_data, [dest])}")

        current_states = next_states
        print(f"Estados após processar '{letter}': {current_states}")

    accepted = any(state in automaton_data["final_states"] for state in current_states)

    return accepted, process

# Calcula o fecho-épsilon para um conjunto de estados, que é um conjunto de estados alcançáveis através de transições epsilon.
def epsilon_closure(automaton, states):
    closure = set(states)
    queue = deque(states)
    while queue:
        state = queue.popleft()
        if state in automaton["transitions"] and '' in automaton["transitions"][state]:
            for next_state in automaton["transitions"][state]['']:
                if next_state not in closure:
                    closure.add(next_state)
                    queue.append(next_state)
    return frozenset(closure)

@app.route('/input_turing_machine')
def input_turing_machine():
    return render_template('input_turing_machine.html')

@app.route('/save_turing_machine', methods=['POST'])
def save_turing_machine():
    global turing_machine
    turing_machine = {
        "states": request.form["states"].split(","),
        "alphabet": request.form["alphabet"].split(","),
        "tape_alphabet": request.form["tape_alphabet"].split(","),
        "transitions": []
    }

    transitions = request.form["transitions"].strip().split("\n")
    for t in transitions:
        state, symbol, next_state, write_symbol, direction = t.split(",")
        turing_machine["transitions"].append({
            "state": state.strip(),
            "symbol": symbol.strip(),
            "next_state": next_state.strip(),
            "write_symbol": write_symbol.strip(),
            "direction": direction.strip()
        })

    turing_machine["initial_state"] = request.form["initial_state"]
    turing_machine["accept_states"] = request.form["accept_states"].split(",")
    turing_machine["reject_states"] = request.form["reject_states"].split(",")

    return redirect(url_for("input_tape"))

@app.route('/input_tape')
def input_tape():
    return render_template('input_tape.html')

@app.route('/process_tape', methods=['POST'])
def process_tape():
    global turing_machine
    tape = request.json["tape"]
    result, process = simulate_turing_machine(turing_machine, tape)
    return jsonify({"result": result, "process": process})

def simulate_turing_machine(turing_machine, input_tape):
    tape = list(input_tape)
    current_state = turing_machine["initial_state"]
    head_position = 0
    process = []

    tape.append("_") 

    while True:
        current_symbol = tape[head_position] if 0 <= head_position < len(tape) else "_"
        transition = next((t for t in turing_machine["transitions"] 
                           if t["state"] == current_state and t["symbol"] == current_symbol), None)

        if transition is None:
            break  

        tape[head_position] = transition["write_symbol"]
        process.append((current_state, current_symbol, transition["write_symbol"], head_position))

        current_state = transition["next_state"]
        if transition["direction"] == "R":
            head_position += 1
        elif transition["direction"] == "L":
            head_position -= 1

        if head_position < 0:
            return "Não", process 
        
        #Verificação de estado de aceitação
        if current_state in turing_machine["accept_states"]:
            return "Sim", process
        elif current_state in turing_machine["reject_states"]:
            return "Não", process

    return "Não", process  # Se não for aceito

@app.route('/get_turing_machine')
def get_turing_machine():
    global turing_machine
    return jsonify(turing_machine)


if __name__ == "__main__":
    app.run(debug=True)