import os

from modules import debugger


def test():
    def bj(bp):
        print bp

    dbg = debugger.Debugger()
    print os.getcwd()
    dbg.load("../tests/crash.exe", "")
    dbg.set_breakpoint(0x004015A5, bj)
    dbg.run()


if __name__ == "__main__":
    test()
