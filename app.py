from flask import Flask, request, render_template, redirect, url_for, jsonify
from collections import defaultdict, deque

app = Flask(__name__)

# Dicionários para armazenar o autômato e o DFA
automaton = {}
dfa = None

@app.route("/")
def input_automaton():
    return render_template("input_automaton.html")

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

def nfa_accepts_word(nfa, word):
    """Verifica se o NFA aceita a palavra dada."""
    current_states = set([nfa["initial_state"]])
    
    for symbol in word:
        next_states = set()
        for state in current_states:
            next_states.update(nfa_transitions(state, symbol, nfa))
        current_states = next_states
    
    # Verifica se algum estado alcançado é final
    return any(state in nfa["final_states"] for state in current_states)

def nfa_transitions(state, symbol, nfa):
    """Retorna os estados alcançáveis por transição no AFN."""
    return {trans[2] for trans in nfa["transitions"] if trans[0] == state and trans[1] == symbol}


@app.route("/check_equivalence", methods=["POST"])
def check_equivalence():
    global automaton, dfa
    word = request.json["word"]
    nfa_accepts = nfa_accepts_word(automaton, word)  # Verifica aceitação no AFN
    dfa_accepts, _ = simulate_dfa(dfa, word)         # Verifica aceitação no AFD
    
    equivalent = nfa_accepts == dfa_accepts  # Verifica se são equivalentes
    
    return jsonify({
        "word": word,
        "nfa_accepts": nfa_accepts,
        "dfa_accepts": dfa_accepts,
        "equivalent": equivalent
    })


@app.route("/minimize_dfa")
def minimize_dfa_view():
    global dfa
    if dfa is None or not is_dfa(dfa):
        return render_template("error.html", message="Não é possível minimizar. Verifique se o autômato é um DFA válido.", automaton=dfa)
    
    minimized_dfa = minimize_dfa(dfa)
    if minimized_dfa is None:
        return render_template("error.html", message="O autômato já está minimizado ou não pode ser minimizado.", automaton=dfa)

    return render_template("dfa_minimized.html", dfa=minimized_dfa)

def minimize_dfa(dfa):
    alphabet = [symbol.strip() for symbol in dfa['alphabet']]
    states = [state.strip() for state in dfa['states']]
    initial_state = dfa['initial_state'].strip()
    final_states = set(state.strip() for state in dfa['final_states'])
    transitions = [(trans[0].strip(), trans[1].strip(), trans[2].strip()) for trans in dfa['transitions']]

    # Construir a tabela de equivalência inicial
    equivalence_table = defaultdict(lambda: defaultdict(bool))

    # Passo 1: Marcar estados finalizados e não finalizados como não equivalentes
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            state1, state2 = states[i], states[j]
            # Se um estado é final e o outro não, são considerados não equivalentes
            if ((state1 in final_states) != (state2 in final_states)) or (state1 in final_states and state2 in final_states):
                equivalence_table[state1][state2] = True

    # Passo 2: Propagar a não-equivalência
    pending = deque()
    for i in range(len(states)):
        for j in range(i+1, len(states)):
            state1, state2 = states[i], states[j]
            if equivalence_table[state1][state2]:
                continue
            for symbol in alphabet:
                next_state1 = next_state2 = None
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
                    else:
                        pending.append((state1, state2, next_state1, next_state2))

    while pending:
        state1, state2, next_state1, next_state2 = pending.popleft()
        if equivalence_table[next_state1][next_state2]:
            equivalence_table[state1][state2] = True

    # Verificar se o DFA já está minimizado
    all_pairs = [(state1, state2) for state1 in states for state2 in states if state1 != state2]
    if all(equivalence_table[state1][state2] for state1, state2 in all_pairs):
        return None  # Retorna None indicando que o DFA não pode ser minimizado mais

    # Passo 3: Agrupar estados equivalentes
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

    # Passo 4: Construir o DFA minimizado
    minimized_states = list(equivalence_classes.keys())
    minimized_transitions = []
    minimized_final_states = [state_to_class[state] for state in final_states]

    # Construir transições únicas para o AFD minimizado
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

    # Passo 5: Identificar estados alcançáveis
    reachable_states = set()
    to_process = [minimized_initial_state]

    while to_process:
        current = to_process.pop()
        if current not in reachable_states:
            reachable_states.add(current)
            for symbol in alphabet:
                for trans in minimized_transitions:
                    if trans[0] == current and trans[1] == symbol:
                        to_process.append(trans[2])

    minimized_transitions = [trans for trans in minimized_transitions if trans[0] in reachable_states]
    minimized_states = [state for state in minimized_states if state in reachable_states]
    minimized_final_states = [state for state in minimized_final_states if state in reachable_states]

    return {
        'alphabet': alphabet,
        'states': minimized_states,
        'initial_state': minimized_initial_state,
        'final_states': list(set(minimized_final_states)),
        'transitions': minimized_transitions
    }



if __name__ == "__main__":
    app.run(debug=True)