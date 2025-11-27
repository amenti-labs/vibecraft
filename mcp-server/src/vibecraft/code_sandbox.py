"""
Safe Python code execution for Minecraft command generation.

Uses Python's built-in ast module for validation and exec() with restricted namespace.
No external dependencies required!
"""

import ast
import math
from typing import List, Dict, Any, Set


class CodeSandboxError(Exception):
    """Raised when code validation or execution fails"""
    pass


# Whitelist of allowed node types for safe code execution
ALLOWED_NODES: Set[type] = {
    # Structural
    ast.Module,
    ast.Expr,
    ast.Assign,
    ast.AugAssign,

    # Control flow
    ast.For,
    ast.If,
    ast.Break,
    ast.Continue,

    # Functions (for code organization)
    ast.FunctionDef,
    ast.Return,
    ast.arguments,
    ast.arg,

    # Expressions
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.BoolOp,
    ast.IfExp,  # Ternary/conditional expressions (x if condition else y)
    ast.Call,
    ast.Attribute,
    ast.Subscript,
    ast.Index,
    ast.Slice,

    # Literals
    ast.Constant,
    ast.Num,
    ast.Str,
    ast.List,
    ast.Tuple,
    ast.Dict,
    ast.Set,

    # Variables
    ast.Name,
    ast.Load,
    ast.Store,

    # Operators
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.Pow,
    ast.Lt,
    ast.Gt,
    ast.LtE,
    ast.GtE,
    ast.Eq,
    ast.NotEq,
    ast.And,
    ast.Or,
    ast.Not,
    ast.USub,

    # List/Dict operations
    ast.ListComp,
    ast.comprehension,

    # String formatting (for f-strings)
    ast.JoinedStr,
    ast.FormattedValue,
}


def validate_code_ast(code: str, max_iterations: int = 100000) -> None:
    """
    Validate Python code AST for safety.

    Ensures code only uses whitelisted operations and doesn't exceed iteration limits.

    Args:
        code: Python code to validate
        max_iterations: Maximum total loop iterations allowed

    Raises:
        CodeSandboxError: If code contains unsafe operations or exceeds limits
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise CodeSandboxError(f"Syntax error in code: {e}")

    # Check all nodes against whitelist
    for node in ast.walk(tree):
        if type(node) not in ALLOWED_NODES:
            raise CodeSandboxError(
                f"Unsafe operation: {type(node).__name__} is not allowed. "
                f"Only basic loops, math, and list operations are permitted."
            )

    # Estimate maximum iterations (rough check)
    total_iterations = 1
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            # Try to estimate range size
            if isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                    args = node.iter.args
                    if len(args) == 1:
                        if isinstance(args[0], ast.Constant):
                            total_iterations *= args[0].value
                    elif len(args) == 2:
                        if isinstance(args[0], ast.Constant) and isinstance(args[1], ast.Constant):
                            total_iterations *= abs(args[1].value - args[0].value)

    if total_iterations > max_iterations:
        raise CodeSandboxError(
            f"Code may execute too many iterations ({total_iterations} > {max_iterations}). "
            f"Please reduce loop sizes."
        )


def execute_command_generator(
    code: str,
    max_commands: int = 10000,
    max_iterations: int = 100000,
    timeout_seconds: int = 5
) -> List[str]:
    """
    Execute Python code that generates Minecraft commands.

    Code must populate a 'commands' list with command strings.
    Only safe operations are allowed (loops, math, strings, lists).

    Args:
        code: Python code that generates commands
        max_commands: Maximum number of commands allowed
        max_iterations: Maximum loop iterations allowed
        timeout_seconds: Execution timeout (not enforced yet, placeholder)

    Returns:
        List of Minecraft command strings

    Raises:
        CodeSandboxError: If code is unsafe or execution fails

    Example:
        >>> code = '''
        ... commands = []
        ... for x in range(100, 110):
        ...     commands.append(f"/setblock {x} 64 200 stone")
        ... '''
        >>> execute_command_generator(code)
        ['/setblock 100 64 200 stone', '/setblock 101 64 200 stone', ...]
    """
    # Validate code first
    validate_code_ast(code, max_iterations)

    # Create restricted namespace
    # Only provide safe built-in functions
    safe_namespace: Dict[str, Any] = {
        'commands': [],
        'range': range,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'round': round,
        'int': int,
        'float': float,
        'str': str,
        'list': list,
        'tuple': tuple,
        'dict': dict,
        'set': set,
        'enumerate': enumerate,
        'zip': zip,
        'sorted': sorted,
        'reversed': reversed,
        'sum': sum,
        'any': any,
        'all': all,
        'print': print,  # Debugging output (safe, no side effects)
        # Math functions (safe, no side effects)
        'sqrt': math.sqrt,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'asin': math.asin,
        'acos': math.acos,
        'atan': math.atan,
        'atan2': math.atan2,
        'radians': math.radians,
        'degrees': math.degrees,
        'pi': math.pi,
        'e': math.e,
        'floor': math.floor,
        'ceil': math.ceil,
        'pow': pow,  # Built-in pow (also accessible via ** operator)
        '__builtins__': {},  # Empty builtins prevents imports, file access, etc.
    }

    # Execute code in restricted environment
    try:
        exec(code, safe_namespace)
    except Exception as e:
        raise CodeSandboxError(f"Code execution failed: {type(e).__name__}: {e}")

    # Extract commands
    commands = safe_namespace.get('commands', [])

    if not isinstance(commands, list):
        raise CodeSandboxError(
            f"Code must create a 'commands' list. Got {type(commands).__name__} instead."
        )

    # Validate command count
    if len(commands) > max_commands:
        raise CodeSandboxError(
            f"Too many commands generated: {len(commands)} > {max_commands}. "
            f"Please reduce the scope."
        )

    # Validate all commands are strings
    for i, cmd in enumerate(commands):
        if not isinstance(cmd, str):
            raise CodeSandboxError(
                f"Command {i} is not a string: {type(cmd).__name__}. "
                f"All commands must be strings."
            )

        # Validate command format (starts with / or //)
        if not cmd.strip().startswith('/'):
            raise CodeSandboxError(
                f"Command {i} doesn't start with '/' or '//': {cmd}"
            )

    return commands


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Simple loop
    code1 = """
commands = []
for x in range(100, 110):
    commands.append(f"/setblock {x} 64 200 stone")
"""

    result1 = execute_command_generator(code1)
    print(f"Example 1: Generated {len(result1)} commands")
    print(f"First command: {result1[0]}")
    print(f"Last command: {result1[-1]}")

    # Example 2: Nested loops with conditionals
    code2 = """
commands = []
for x in range(100, 110):
    for y in range(64, 74):
        for z in range(200, 210):
            # Only place blocks in a sphere
            distance = ((x-105)**2 + (y-69)**2 + (z-205)**2)**0.5
            if distance < 5:
                commands.append(f"/setblock {x} {y} {z} red_concrete")
"""

    result2 = execute_command_generator(code2)
    print(f"\nExample 2: Generated {len(result2)} commands (sphere)")

    # Example 3: Error - unsafe operation
    code3 = """
commands = []
import os  # Not allowed!
"""

    try:
        execute_command_generator(code3)
    except CodeSandboxError as e:
        print(f"\nExample 3: Correctly blocked unsafe code: {e}")
