from flask import Flask, request, jsonify
from flask_cors import CORS
from sympy.parsing.latex import parse_latex

app = Flask(__name__)
CORS(app)

@app.route('/api/process', methods=['POST'])
def check_variables():
    data = request.get_json()
    formula = data.get('formula', '')
    uncertainties = data.get('uncertainties', '')

    formula = parse_latex(formula)
    variables = {str(s): s for s in formula.free_symbols}
    variables = {key: str(value) for key, value in variables.items()}
    print(variables)

    uncertainties = parse_latex(uncertainties)
    uncertain_vars = {str(s): s for s in uncertainties.free_symbols}
    uncertain_vars = {key: str(value) for key, value in uncertain_vars.items()}
    print(uncertain_vars)

    return jsonify({'formula': ", ".join(str(value) for value in variables.values()), 'uncertainties': ", ".join(str(value) for value in uncertain_vars.values())})

if __name__ == '__main__':
    app.run(debug=True)
