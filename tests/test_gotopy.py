import unittest
from typing import Dict, Any, Callable, List
from gotopy2.gotopy import run_program, ProgramType


class TestGotoPy(unittest.TestCase):

    def test_lambda_style_program(self) -> None:
        # Classic style: no ProgramType, just lambdas
        prog = {
            10: lambda g, r: g.update(x=1),
            20: lambda g, r: g.update(x=g['x'] + 1),
            30: lambda g, r: None,
        }
        g: Dict[str, Any] = {}
        run_program(prog, g)
        self.assertEqual(g['x'], 2)

    def test_sequential(self) -> None:

        def step10(g: Dict[str, Any], r: Any) -> None:
            g.update(x=1)

        def step20(g: Dict[str, Any], r: Any) -> None:
            g.update(x=g["x"] + 1)

        def step30(g: Dict[str, Any], r: Any) -> None:
            pass

        prog: ProgramType = {
            10: step10,
            20: step20,
            30: step30,
        }
        g: Dict[str, Any] = {}
        run_program(prog, g)
        self.assertEqual(g["x"], 2)

    def test_goto(self) -> None:
        def step10(g: Dict[str, Any], r: Any) -> None:
            g.update(x=1)

        def step20(g: Dict[str, Any], r: Any) -> None:
            r.goto(40)

        def step30(g: Dict[str, Any], r: Any) -> None:
            g.update(x=999)  # skipped

        def step40(g: Dict[str, Any], r: Any) -> None:
            g.update(x=g["x"] + 5)

        prog: ProgramType = {
            10: step10,
            20: step20,
            30: step30,
            40: step40,
        }
        g: Dict[str, Any] = {}
        run_program(prog, g)
        self.assertEqual(g["x"], 6)

    def test_gosub_return(self) -> None:
        trace: List[int] = []

        def step10(g: Dict[str, Any], r: Any) -> None:
            trace.append(10)
            g.update(x=1)

        def step20(g: Dict[str, Any], r: Any) -> None:
            trace.append(20)
            r.gosub(50)

        def step30(g: Dict[str, Any], r: Any) -> None:
            trace.append(30)
            g.update(done=True)
            r.halt()

        def step50(g: Dict[str, Any], r: Any) -> None:
            trace.append(50)
            g.update(x=g["x"] * 10)

        def step60(g: Dict[str, Any], r: Any) -> None:
            trace.append(60)
            r.return_()

        prog: ProgramType = {
            10: step10,
            20: step20,
            30: step30,
            50: step50,
            60: step60,
        }
        g: Dict[str, Any] = {}
        run_program(prog, g)
        self.assertEqual(trace, [10, 20, 50, 60, 30])
        self.assertEqual(g["x"], 10)
        self.assertTrue(g["done"])

    def test_multiple_gosubs(self) -> None:
        trace: List[int] = []

        def step10(g: Dict[str, Any], r: Any) -> None:
            trace.append(10)
            r.gosub(100)

        def step20(g: Dict[str, Any], r: Any) -> None:
            trace.append(20)
            r.gosub(200)

        def step30(g: Dict[str, Any], r: Any) -> None:
            trace.append(30)
            r.halt()

        def step100(g: Dict[str, Any], r: Any) -> None:
            trace.append(100)
            r.return_()

        def step200(g: Dict[str, Any], r: Any) -> None:
            trace.append(200)
            r.return_()

        prog: ProgramType = {
            10: step10,
            20: step20,
            30: step30,
            100: step100,
            200: step200,
        }
        run_program(prog)
        self.assertEqual(trace, [10, 100, 20, 200, 30])

    def test_nested_gosubs(self) -> None:
        trace: List[int] = []

        def step10(g: Dict[str, Any], r: Any) -> None:
            trace.append(10)
            r.gosub(100)

        def step20(g: Dict[str, Any], r: Any) -> None:
            trace.append(20)
            r.halt()

        def step100(g: Dict[str, Any], r: Any) -> None:
            trace.append(100)
            r.gosub(200)

        def step110(g: Dict[str, Any], r: Any) -> None:
            trace.append(110)
            r.return_()

        def step200(g: Dict[str, Any], r: Any) -> None:
            trace.append(200)
            r.return_()

        prog: ProgramType = {
            10: step10,
            20: step20,
            100: step100,
            110: step110,
            200: step200,
        }
        run_program(prog)
        self.assertEqual(trace, [10, 100, 200, 110, 20])

    def test_goto_loop(self) -> None:
        g: Dict[str, int] = {"n": 0}

        def step10(g: Dict[str, int], r: Any) -> None:
            g["n"] = g["n"] + 1

        def step20(g: Dict[str, int], r: Any) -> None:
            if g["n"] < 3:
                r.goto(10)
            else:
                r.halt()

        prog: Dict[int, Callable[[Dict[str, int], Any], None]] = {
            10: step10,
            20: step20,
        }
        run_program(prog, g)
        self.assertEqual(g["n"], 3)

    def test_return_without_gosub(self) -> None:
        prog: Dict[int, Callable[[Dict[str, Any], Any], None]] = {
            10: lambda g, r: r.return_(),
        }
        with self.assertRaises(RuntimeError):
            run_program(prog)

    def test_halt(self) -> None:
        prog: Dict[int, Callable[[Dict[str, Any], Any], None]] = {
            10: lambda g, r: g.update(x=1),
            20: lambda g, r: r.halt(),
            30: lambda g, r: g.update(x=999),  # should not run
        }
        g: Dict[str, Any] = {}
        run_program(prog, g)
        self.assertEqual(g["x"], 1)
        self.assertNotIn("999", g.values())

    # Note: run_file requires a physical file, so it's not tested here.


if __name__ == "__main__":
    unittest.main()
