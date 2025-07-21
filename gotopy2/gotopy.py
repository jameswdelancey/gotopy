"""
Minimalist GOTO/GOSUB interpreter with line numbering (CBMBASIC style).
Each program is a dict: {line_number: callable(globals, runtime)}
"""

from typing import Any, Callable, Dict, Optional, List
import importlib.util
import sys


ProgramType = Dict[int, Callable[[Dict[str, Any], "Runtime"], None]]


class Runtime:
    program: ProgramType
    lines: List[int]
    line_idx: int
    stack: List[Optional[int]]
    globals: Dict[str, Any]
    parent: Optional["Runtime"]
    _goto_line: Optional[int]
    _returning: bool
    _halted: bool

    def __init__(
        self,
        program: ProgramType,
        globals_dict: Optional[Dict[str, Any]] = None,
        parent: Optional["Runtime"] = None,
    ) -> None:
        self.program = program
        self.lines = sorted(program)
        self.line_idx = 0
        self.stack: List[Optional[int]] = []
        self.globals = globals_dict if globals_dict is not None else {}
        self.parent = parent  # For nested run_file
        self._goto_line: Optional[int] = None
        self._returning = False
        self._halted = False

    def goto(self, line: int) -> None:
        if line not in self.program:
            raise ValueError(f"No such line: {line}")
        self._goto_line = line

    def gosub(self, line: int) -> None:
        if line not in self.program:
            raise ValueError(f"No such line: {line}")
        # Save the next line number (not just index+1)
        if self.line_idx + 1 < len(self.lines):
            next_line = self.lines[self.line_idx + 1]
        else:
            next_line = None
        self.stack.append(next_line)
        self._goto_line = line

    def return_(self) -> None:
        if not self.stack:
            raise RuntimeError("RETURN without GOSUB")
        ret = self.stack.pop()
        if ret is None:
            self._halted = True
        else:
            self._goto_line = ret
        self._returning = True

    def run_file(
        self, filename: str, globals_dict: Optional[Dict[str, Any]] = None
    ) -> None:
        """Load and run another gotopy file (must define 'program')."""
        spec = importlib.util.spec_from_file_location("gotopyfile", filename)
        if spec is None:
            raise ImportError(f"Could not load spec for {filename}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["gotopyfile"] = mod
        if spec.loader is None:
            raise ImportError(f"Spec loader is None for {filename}")
        spec.loader.exec_module(mod)
        if not hasattr(mod, "program"):
            raise ValueError(f"File {filename} must define a 'program' dict.")
        sub_runtime = Runtime(mod.program, globals_dict or self.globals, parent=self)
        sub_runtime.run()
        # After return, globals are shared (by default)

    def halt(self) -> None:
        self._halted = True

    def run(self) -> None:
        self.line_idx = 0
        while self.line_idx < len(self.lines):
            if self._halted:
                break
            line = self.lines[self.line_idx]
            self._goto_line = None
            self._returning = False
            jumped = False
            stmt = self.program[line]
            stmt(self.globals, self)
            if self._halted:
                break
            if self._goto_line is not None:
                self.line_idx = self.lines.index(self._goto_line)
                jumped = True
            elif self._returning:
                if self._halted:
                    break
                if self._goto_line is not None:
                    self.line_idx = self.lines.index(self._goto_line)
                    jumped = True
                else:
                    break
            if not jumped:
                # Move to the next higher line number, or halt if none
                if self.line_idx + 1 < len(self.lines):
                    self.line_idx += 1
                else:
                    break


def run_program(
    program: ProgramType, globals_dict: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Run a gotopy program dict."""
    rt = Runtime(program, globals_dict)
    rt.run()
    return rt.globals
