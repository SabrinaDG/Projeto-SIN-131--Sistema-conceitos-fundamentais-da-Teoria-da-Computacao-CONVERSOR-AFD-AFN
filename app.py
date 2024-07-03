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
    automaton["type"] = request.form["automaton_type"]  # Tipo de autômato
    automaton["alphabet"] = request.form["alphabet"].split(",")
    automaton["states"] = request.form["states"].split(",")
    automaton["initial_state"] = request.form["initial_state"]
    automaton["final_states"] = request.form["final_states"].split(",")
    transitions = request.form["transitions"].strip().split("\n")
    automaton["transitions"] = [t.split(",") for t in transitions]

    if automaton["type"] == "AFD":
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
    return render_template("dfa_result.html", dfa=dfa, show_table=True)

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
    automaton.clear()  # Reseta o autômato
    dfa = None  # Reseta o DFA
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
        'final_states': list(final_states),  # Lista real de estados finais
        'transitions': [(k[0], k[1], v) for k, v in dfa_transitions.items()]
    }

if __name__ == "__main__":
    app.run(debug=True)
