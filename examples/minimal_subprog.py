from gotopy2 import ProgramType

program: ProgramType = {
    10: lambda g, r: g.update(msg="Hello from subprogram!"),
    20: lambda g, r: r.halt(),
}
