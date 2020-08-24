import sys


def logInfo(s):
    print("[-]", s)
    sys.stdout.flush()


def logStep(s):
    print("[+]", s)
    sys.stdout.flush()


def logWarn(s):
    print("[!]", s)
    sys.stdout.flush()


def logErr(s):
    print("[X]", s)
    sys.stdout.flush()
