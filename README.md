# gotopy

A minimalist, modern Python interpreter and library for CBMBASIC-style control flow using line numbers, `GOTO`, `GOSUB`, and `RETURN`.

- Programs are Python dicts mapping line numbers to functions or lambdas.
- Each line operates on a shared `globals` dict and a `runtime` object.
- Supports `GOTO`, `GOSUB`, `RETURN`, `HALT`, and calling other gotopy files (`run_file`).
- Designed for educational, retro, and DSL experiments.

## Features
- Sequential line-numbered execution (like BASIC)
- `goto(line)`, `gosub(line)`, `return_()` for control flow
- `halt()` to stop execution
- `run_file(filename)` to load and run other gotopy programs
- Type-safe: ships with `ProgramType` for static analysis
- Fully tested and type-checked

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. To install:

```bash
poetry install
```

## Usage Example

### Modern, type-annotated style
```python
from gotopy import run_program, ProgramType

program: ProgramType = {
    10: lambda g, r: g.update(x=1),
    20: lambda g, r: print('X is', g['x']),
    30: lambda g, r: r.goto(50) if g['x'] < 3 else r.halt(),
    40: lambda g, r: r.halt(),
    50: lambda g, r: g.update(x=g['x']+1),
}

run_program(program)
```

### Classic lambda style (backward compatible)
```python
# You can also use the classic style with plain lambdas and no type annotations:
program = {
    10: lambda g, r: g.update(x=1),
    20: lambda g, r: g.update(x=g['x'] + 1),
    30: lambda g, r: None,
}
g = {}
run_program(program, g)
```
Both styles are tested and supported.

## Writing Programs
- Each line is a lambda or function: `lambda globals, runtime: ...`
- Use `runtime.goto(line)`, `runtime.gosub(line)`, `runtime.return_()`, `runtime.halt()` for control flow.
- Use `runtime.run_file(filename)` to call another gotopy file (must define a `program` dict).

### Example: Nested `run_file` usage
You can run a subprogram from a main program using `run_file`. The subprogram should halt itself when done.

**main.py**
```python
from gotopy import run_program

def step10(g, r):
    # Import and run a subprogram from the tests directory
    import os
    subprog_path = os.path.join(os.path.dirname(__file__), "tests", "subprog.py")
    r.run_file(subprog_path, g)
def step20(g, r):
    g['done'] = True
    r.halt()
program = {
    10: step10,
    20: step20,
}
g = {}
run_program(program, g)
print(g['msg'])  # Output: hello from subprog
```

**tests/subprog.py**
```python
program = {
    100: lambda g, r: g.update(msg='hello from subprog'),
    110: lambda g, r: r.halt(),
}
```

## Example: GOSUB/RETURN

```python
from gotopy import run_program, ProgramType

program: ProgramType = {
    10: lambda g, r: r.gosub(100),
    20: lambda g, r: print('Back from subroutine!') or r.halt(),
    100: lambda g, r: print('In subroutine'),
    110: lambda g, r: r.return_(),
}
run_program(program)
```

## Testing

Run all tests:
```bash
poetry run python3 -m unittest discover tests
```

## Type Checking & Linting

Run type checks and linting:
```bash
poetry run mypy .
poetry run flake8
```

## Directory Structure

```
gotopy/
├── gotopy/
│   ├── __init__.py
│   └── gotopy.py
├── tests/
│   ├── __init__.py
│   ├── test_gotopy.py
│   ├── test_nested_run_file_subprog.py
│   └── subprog.py
├── pyproject.toml
├── .flake8
├── mypy.ini
└── README.md
```

## License
MIT
