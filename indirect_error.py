import sympy as sp
import io
import matplotlib.pyplot as plt
from sympy.parsing.latex import parse_latex


def compute_uncertainty(formula_str, uncertain_vars):
    formula = parse_latex(formula_str)

    variables = {str(s): s for s in formula.free_symbols}
    for var in variables.values():
        variables[str(var)] = sp.Symbol(str(var), real=True, positive=True)

    formula = formula.subs(variables)

    uncertain_vars_input = parse_latex(uncertain_vars)
    uncertain_vars = {str(s): s for s in uncertain_vars_input.free_symbols}

    partial_derivatives = {}
    for var in uncertain_vars:
        partial_derivatives[var] = sp.diff(formula, variables[var])

    variance = 0
    for var in uncertain_vars:
        uncertainty_symbol = sp.Symbol(f'delta_{var}', real=True, positive=True)
        partial_derivative = partial_derivatives[var]
        variance_contribution = (partial_derivative * uncertainty_symbol) ** 2
        variance += variance_contribution

    total_uncertainty = sp.sqrt(variance)
    total_uncertainty = sp.radsimp(total_uncertainty)
    total_uncertainty = sp.simplify(total_uncertainty)
    total_uncertainty = sp.latex(total_uncertainty)
    return total_uncertainty


def visualize_latex(latex_str, output_filename='latex_output.png'):
    plt.figure()
    plt.text(0.5, 0.5, f"${latex_str}$", fontsize=40, ha='center', va='center')
    plt.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, bbox_inches='tight', pad_inches=0.1, format='png')
    plt.close()
    buf.seek(0)
    return buf
