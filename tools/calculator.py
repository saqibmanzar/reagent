from sympy import sympify

def calculator_tool(expression: str):
    try:
        result = sympify(expression, evaluate=True, rational=False)
        return str(result)
    except Exception as e:
        raise ValueError(f"Calculator failed: {expression}") from e
      