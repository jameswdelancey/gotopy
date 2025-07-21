import tempfile
import os
import unittest
from gotopy2 import run_program, ProgramType
from typing import Dict, Any


class TestNestedRunFile(unittest.TestCase):
    def test_nested_run_file(self) -> None:
        # Subprogram to be called via run_file
        subprog_code = """
program = {
    100: lambda g, r: g.update(msg="hello from subprog"),
    110: lambda g, r: r.halt(),
}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            subprog_path = os.path.join(tmpdir, "subprog.py")
            with open(subprog_path, "w") as f:
                f.write(subprog_code)

            def step10(g: Dict[str, Any], r: Any) -> None:
                r.run_file(subprog_path, g)

            def step20(g: Dict[str, Any], r: Any) -> None:
                g["done"] = True
                r.halt()

            prog: ProgramType = {
                10: step10,
                20: step20,
            }
            g: Dict[str, Any] = {}
            run_program(prog, g)
            self.assertEqual(g["msg"], "hello from subprog")
            self.assertTrue(g["done"])


if __name__ == "__main__":
    unittest.main()
