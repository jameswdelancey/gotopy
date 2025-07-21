import os
from gotopy import run_program
from typing import Dict, Any
from gotopy import ProgramType


def step10(g: Dict[str, Any], r: Any) -> None:
    # Find the subprogram in the examples directory
    subprog_path = os.path.join(os.path.dirname(__file__), "minimal_subprog.py")
    r.run_file(subprog_path, g)


def step20(g: Dict[str, Any], r: Any) -> None:
    g["done"] = True
    r.halt()


program: ProgramType = {
    10: step10,
    20: step20,
}
g: Dict[str, Any] = {}
run_program(program, g)
print(g["msg"])  # Output: Hello from subprogram!
