"""
Safe Python code execution for Minecraft command generation.

Uses Python's built-in ast module for validation and exec() with restricted namespace.
Includes multiple layers of security:
1. AST whitelist - Only allow safe syntax constructs
2. Restricted namespace - No access to dangerous builtins
3. Blocked attribute access - Prevent __class__, __mro__, etc.
4. Resource limits - Maximum commands, iterations, and code length
5. Timeout enforcement - Prevent infinite loops

No external dependencies required!
"""

import ast
import math
import signal
import sys
from contextlib import contextmanager
from typing import List, Dict, Any, Set

from .exceptions import CodeSandboxError, SandboxTimeoutError


# Dangerous attribute names that should never be accessed
BLOCKED_ATTRIBUTES: Set[str] = {
    # Class/type introspection (escape vectors)
    "__class__",
    "__base__",
    "__bases__",
    "__mro__",
    "__subclasses__",
    "__init__",
    "__new__",
    "__del__",
    "__init_subclass__",
    "__class_getitem__",
    "__prepare__",
    # Code execution vectors
    "__code__",
    "__globals__",
    "__locals__",
    "__builtins__",
    "__call__",
    "__self__",
    "__func__",
    # Descriptor/attribute manipulation
    "__getattr__",
    "__getattribute__",
    "__setattr__",
    "__delattr__",
    "__get__",
    "__set__",
    "__delete__",
    "__set_name__",
    # Import system
    "__import__",
    "__loader__",
    "__spec__",
    "__path__",
    "__file__",
    "__cached__",
    "__package__",
    "__name__",
    "__qualname__",
    # Memory/object manipulation
    "__reduce__",
    "__reduce_ex__",
    "__getstate__",
    "__setstate__",
    "__sizeof__",
    "__weakref__",
    "__slots__",
    # Other dangerous attributes
    "func_globals",
    "func_code",
    "gi_frame",
    "gi_code",
    "co_code",
    "f_globals",
    "f_locals",
    "f_builtins",
}

# Blocked function names that shouldn't be callable even if in namespace
BLOCKED_FUNCTION_NAMES: Set[str] = {
    "eval",
    "exec",
    "compile",
    "open",
    "input",
    "__import__",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
    "type",
    "object",
    "super",
    "classmethod",
    "staticmethod",
    "property",
    "memoryview",
    "bytearray",
    "bytes",
    "breakpoint",
    "help",
    "exit",
    "quit",
}


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
    # Expressions
    ast.BinOp,
    ast.UnaryOp,
    ast.Compare,
    ast.BoolOp,
    ast.IfExp,  # Ternary/conditional expressions (x if condition else y)
    ast.Call,
    ast.Subscript,
    ast.Slice,
    ast.Attribute,  # For list.append(), etc. - blocked attrs checked separately
    # Literals
    ast.Constant,
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
    ast.UAdd,
    # List operations (NO dict/set comprehensions - potential abuse)
    ast.ListComp,
    ast.comprehension,
    # String formatting (for f-strings)
    ast.JoinedStr,
    ast.FormattedValue,
}

# NOTE: Explicitly NOT allowed:
# - ast.FunctionDef (prevents function definitions that could escape)
# - ast.Return (not needed without functions)
# - ast.Import, ast.ImportFrom (no imports)
# - ast.With (no context managers)
# - ast.Try, ast.Raise (no exception handling - simplifies security)
# - ast.Global, ast.Nonlocal (no scope manipulation)
# - ast.Lambda (prevents lambda escapes)
# - ast.GeneratorExp, ast.DictComp, ast.SetComp (reduce attack surface)
# - ast.Yield, ast.YieldFrom (no generators)
# - ast.Await, ast.AsyncFor, ast.AsyncWith (no async)
# - ast.Match (no pattern matching - complex semantics)


def validate_code_ast(
    code: str,
    max_iterations: int = 100000,
    max_code_length: int = 50000,
    max_nesting_depth: int = 10,
) -> None:
    """
    Validate Python code AST for safety.

    Performs multiple security checks:
    1. Code length limit
    2. AST node whitelist
    3. Blocked function name check
    4. Iteration limit estimation
    5. Nesting depth limit

    Args:
        code: Python code to validate
        max_iterations: Maximum total loop iterations allowed
        max_code_length: Maximum code length in characters
        max_nesting_depth: Maximum nesting depth for loops/conditions

    Raises:
        CodeSandboxError: If code contains unsafe operations or exceeds limits
    """
    # Check code length
    if len(code) > max_code_length:
        raise CodeSandboxError(f"Code too long: {len(code)} chars > {max_code_length} max")

    # Check for obvious dangerous strings before parsing
    dangerous_strings = [
        "__class__",
        "__mro__",
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__import__",
        "__code__",
        "eval(",
        "exec(",
        "compile(",
        "open(",
        "getattr(",
        "setattr(",
    ]
    code_lower = code.lower()
    for danger in dangerous_strings:
        if danger.lower() in code_lower:
            raise CodeSandboxError(f"Forbidden pattern detected in code: '{danger}'")

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise CodeSandboxError(f"Syntax error in code: {e}")

    # Check all nodes against whitelist and for blocked names
    for node in ast.walk(tree):
        node_type = type(node)

        # Check whitelist
        if node_type not in ALLOWED_NODES:
            raise CodeSandboxError(
                f"Unsafe operation: {node_type.__name__} is not allowed. "
                f"Only basic loops, math, and list operations are permitted."
            )

        # Check for calls to blocked functions
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                if node.func.id in BLOCKED_FUNCTION_NAMES:
                    raise CodeSandboxError(
                        f"Blocked function call: {node.func.id}() is not allowed"
                    )

        # Check for blocked attribute access (e.g., obj.__class__)
        if isinstance(node, ast.Attribute):
            if node.attr in BLOCKED_ATTRIBUTES:
                raise CodeSandboxError(f"Blocked attribute access: .{node.attr} is not allowed")

        # Check for access to blocked names via subscript
        if isinstance(node, ast.Subscript):
            if isinstance(node.slice, ast.Constant):
                if isinstance(node.slice.value, str):
                    if node.slice.value in BLOCKED_ATTRIBUTES:
                        raise CodeSandboxError(
                            f"Blocked attribute access via subscript: ['{node.slice.value}']"
                        )

        # Check variable names for suspicious patterns
        if isinstance(node, ast.Name):
            name = node.id
            if name.startswith("__") and name.endswith("__"):
                raise CodeSandboxError(f"Dunder variable access not allowed: {name}")
            if name in BLOCKED_FUNCTION_NAMES:
                raise CodeSandboxError(f"Access to blocked name: {name}")

    # Check nesting depth
    def check_depth(node: ast.AST, current_depth: int = 0) -> int:
        """Recursively check nesting depth."""
        if current_depth > max_nesting_depth:
            raise CodeSandboxError(f"Code nesting too deep: {current_depth} > {max_nesting_depth}")

        max_child_depth = current_depth
        for child in ast.iter_child_nodes(node):
            # Increase depth for loops and conditions
            child_depth = current_depth
            if isinstance(child, (ast.For, ast.If, ast.ListComp)):
                child_depth = current_depth + 1

            result = check_depth(child, child_depth)
            max_child_depth = max(max_child_depth, result)

        return max_child_depth

    check_depth(tree)

    # Estimate maximum iterations (rough check)
    total_iterations = 1
    for node in ast.walk(tree):
        if isinstance(node, ast.For):
            # Try to estimate range size
            if isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    args = node.iter.args
                    if len(args) == 1:
                        if isinstance(args[0], ast.Constant):
                            val = args[0].value
                            if isinstance(val, int) and val > 0:
                                total_iterations *= val
                    elif len(args) >= 2:
                        if isinstance(args[0], ast.Constant) and isinstance(args[1], ast.Constant):
                            start = args[0].value
                            end = args[1].value
                            if isinstance(start, int) and isinstance(end, int):
                                total_iterations *= abs(end - start)

    if total_iterations > max_iterations:
        raise CodeSandboxError(
            f"Code may execute too many iterations ({total_iterations:,} > {max_iterations:,}). "
            f"Please reduce loop sizes."
        )


@contextmanager
def _timeout_context(seconds: int):
    """Context manager for timeout enforcement on Unix systems."""

    def _timeout_handler(signum, frame):
        raise SandboxTimeoutError(f"Code execution timed out after {seconds} seconds")

    # Only use signal-based timeout on Unix (not Windows)
    if sys.platform != "win32" and seconds > 0:
        old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    else:
        # On Windows or timeout=0, no timeout enforcement
        yield


def _create_safe_namespace() -> Dict[str, Any]:
    """Create a restricted namespace for code execution.

    Returns a namespace with only safe, side-effect-free functions.
    All dangerous builtins are explicitly excluded.
    """

    # Create safe wrappers for some functions to prevent abuse
    def safe_range(*args):
        """Safe range that limits maximum size."""
        if len(args) == 1:
            stop = args[0]
            if not isinstance(stop, int) or stop > 10000:
                raise CodeSandboxError(f"range stop value too large: {stop}")
            return range(stop)
        elif len(args) == 2:
            start, stop = args
            if not isinstance(start, int) or not isinstance(stop, int):
                raise CodeSandboxError("range arguments must be integers")
            if abs(stop - start) > 10000:
                raise CodeSandboxError(f"range size too large: {abs(stop - start)}")
            return range(start, stop)
        elif len(args) == 3:
            start, stop, step = args
            if not all(isinstance(x, int) for x in [start, stop, step]):
                raise CodeSandboxError("range arguments must be integers")
            if step == 0:
                raise CodeSandboxError("range step cannot be zero")
            size = abs((stop - start) // step)
            if size > 10000:
                raise CodeSandboxError(f"range size too large: {size}")
            return range(start, stop, step)
        else:
            raise CodeSandboxError("range takes 1-3 arguments")

    def safe_print(*args, **kwargs):
        """Safe print that does nothing (prevents output abuse)."""
        pass  # Silently ignore - we don't want arbitrary output

    return {
        # Output list (will be populated by code)
        "commands": [],
        # Safe iterables
        "range": safe_range,
        "enumerate": enumerate,
        "zip": zip,
        "sorted": sorted,
        "reversed": reversed,
        # Safe aggregations
        "len": len,
        "sum": sum,
        "min": min,
        "max": max,
        "any": any,
        "all": all,
        # Safe type conversions (primitives only)
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        # Safe constructors (empty only, filled via literals)
        "list": list,
        "tuple": tuple,
        "dict": dict,
        "set": set,
        # Safe math
        "abs": abs,
        "round": round,
        "pow": pow,
        # Math module functions (all pure, no side effects)
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "radians": math.radians,
        "degrees": math.degrees,
        "floor": math.floor,
        "ceil": math.ceil,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        # Math constants
        "pi": math.pi,
        "e": math.e,
        # Safe output (no-op)
        "print": safe_print,
        # CRITICAL: Empty builtins prevents access to dangerous functions
        "__builtins__": {},
    }


def execute_command_generator(
    code: str,
    max_commands: int = 10000,
    max_iterations: int = 100000,
    timeout_seconds: int = 5,
) -> List[str]:
    """
    Execute Python code that generates Minecraft commands.

    Code must populate a 'commands' list with command strings.
    Only safe operations are allowed (loops, math, strings, lists).

    Security measures:
    - AST whitelist validation
    - Blocked function/attribute checks
    - Restricted namespace (no dangerous builtins)
    - Timeout enforcement (Unix only)
    - Output size limits

    Args:
        code: Python code that generates commands
        max_commands: Maximum number of commands allowed (default 10000)
        max_iterations: Maximum loop iterations allowed (default 100000)
        timeout_seconds: Execution timeout in seconds (default 5, Unix only)

    Returns:
        List of Minecraft command strings

    Raises:
        CodeSandboxError: If code is unsafe or execution fails
        SandboxTimeoutError: If code execution times out

    Example:
        >>> code = '''
        ... commands = []
        ... for x in range(100, 110):
        ...     commands.append(f"/setblock {x} 64 200 stone")
        ... '''
        >>> execute_command_generator(code)
        ['/setblock 100 64 200 stone', '/setblock 101 64 200 stone', ...]
    """
    # Validate code first (AST analysis)
    validate_code_ast(code, max_iterations)

    # Create restricted namespace
    safe_namespace = _create_safe_namespace()

    # Execute code in restricted environment with timeout
    try:
        with _timeout_context(timeout_seconds):
            exec(code, safe_namespace)
    except SandboxTimeoutError:
        raise  # Re-raise timeout errors
    except CodeSandboxError:
        raise  # Re-raise our own errors
    except Exception as e:
        # Wrap other exceptions to not leak internal details
        error_type = type(e).__name__
        error_msg = str(e)
        # Sanitize error message to prevent information leakage
        if len(error_msg) > 200:
            error_msg = error_msg[:200] + "..."
        raise CodeSandboxError(f"Code execution failed: {error_type}: {error_msg}")

    # Extract commands
    commands = safe_namespace.get("commands", [])

    if not isinstance(commands, list):
        raise CodeSandboxError(
            f"Code must create a 'commands' list. Got {type(commands).__name__} instead."
        )

    # Validate command count
    if len(commands) > max_commands:
        raise CodeSandboxError(
            f"Too many commands generated: {len(commands):,} > {max_commands:,}. "
            f"Please reduce the scope."
        )

    # Validate all commands
    validated_commands: List[str] = []
    for i, cmd in enumerate(commands):
        if not isinstance(cmd, str):
            raise CodeSandboxError(
                f"Command {i} is not a string: {type(cmd).__name__}. "
                f"All commands must be strings."
            )

        cmd = cmd.strip()

        # Check command length
        if len(cmd) > 1000:
            raise CodeSandboxError(f"Command {i} too long: {len(cmd)} chars > 1000 max")

        # Validate command format (starts with / or //)
        if not cmd.startswith("/"):
            raise CodeSandboxError(f"Command {i} doesn't start with '/': {cmd[:50]}...")

        # Check for potentially dangerous command patterns
        cmd_lower = cmd.lower()
        dangerous_patterns = [
            "stop",
            "ban",
            "kick",
            "op ",
            "deop",
            "whitelist",
            "save-all",
            "save-off",
            "save-on",
            "reload",
        ]
        for pattern in dangerous_patterns:
            if pattern in cmd_lower:
                raise CodeSandboxError(
                    f"Command {i} contains blocked pattern '{pattern}': {cmd[:50]}..."
                )

        validated_commands.append(cmd)

    return validated_commands


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("VibeCraft Code Sandbox - Security Tests")
    print("=" * 60)

    # Example 1: Simple loop (should work)
    print("\n[TEST 1] Simple loop - should succeed")
    code1 = """
commands = []
for x in range(100, 110):
    commands.append(f"/setblock {x} 64 200 stone")
"""
    try:
        result1 = execute_command_generator(code1)
        print(f"  ✅ Generated {len(result1)} commands")
        print(f"  First: {result1[0]}")
    except CodeSandboxError as e:
        print(f"  ❌ Unexpected error: {e}")

    # Example 2: Nested loops with math (should work)
    print("\n[TEST 2] Nested loops with sphere math - should succeed")
    code2 = """
commands = []
for x in range(100, 110):
    for y in range(64, 74):
        for z in range(200, 210):
            distance = sqrt((x-105)**2 + (y-69)**2 + (z-205)**2)
            if distance < 5:
                commands.append(f"/setblock {x} {y} {z} red_concrete")
"""
    try:
        result2 = execute_command_generator(code2)
        print(f"  ✅ Generated {len(result2)} commands (sphere)")
    except CodeSandboxError as e:
        print(f"  ❌ Unexpected error: {e}")

    # Security tests - these should all fail
    print("\n" + "=" * 60)
    print("Security Tests - All should be blocked")
    print("=" * 60)

    security_tests = [
        ("Import statement", "commands = []\nimport os"),
        ("__class__ access", "commands = []\nx = ''.__class__"),
        ("__mro__ access", "commands = []\nx = ''.__class__.__mro__"),
        ("eval() call", "commands = []\neval('1+1')"),
        ("exec() call", "commands = []\nexec('pass')"),
        ("open() call", "commands = []\nopen('/etc/passwd')"),
        ("getattr() call", "commands = []\ngetattr(str, 'upper')"),
        ("Function definition", "commands = []\ndef foo(): pass"),
        ("Lambda expression", "commands = []\nf = lambda x: x"),
        ("Dunder variable", "commands = []\n__name__"),
        ("Range too large", "commands = []\nfor i in range(1000000): pass"),
        ("Dangerous command", "commands = ['/stop']"),
        ("Server command", "commands = ['/ban player']"),
    ]

    for name, code in security_tests:
        try:
            execute_command_generator(code)
            print(f"  ❌ FAILED: {name} was NOT blocked!")
        except (CodeSandboxError, SandboxTimeoutError):
            print(f"  ✅ Blocked: {name}")

    print("\n" + "=" * 60)
    print("Security tests complete")
    print("=" * 60)
