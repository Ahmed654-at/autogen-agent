"""Simple tools the agent can call. AutoGen reads the type hints and docstrings."""

import ast
import operator
from datetime import datetime

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def get_current_time() -> str:
    """Return the current local date and time, e.g. '2026-10-01 18:45:12 (Thursday)'."""
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z (%A)")


def _evaluate(node: ast.AST) -> int | float:
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("Exponent too large.")
        return _BINARY_OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Only numbers and + - * / // % ** and parentheses are allowed.")


def calculator(expression: str) -> str:
    """Safely evaluate a math expression such as '2345 * 67' or '(3 + 4) ** 2' and return the result."""
    try:
        expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        result = _evaluate(ast.parse(expression, mode="eval").body)
    except (SyntaxError, ValueError, ZeroDivisionError, OverflowError) as error:
        return f"Error: could not evaluate '{expression}': {error}"
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return str(result)
