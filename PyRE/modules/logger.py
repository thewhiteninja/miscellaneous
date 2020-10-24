import sys

DEBUG, INFO, WARNING, ERROR, NONE = 0, 1, 2, 3, 4

_logLevel = 1


def logLevel(level):
    global _logLevel
    _logLevel = level


def logDebug(s):
    if _logLevel < INFO:
        print '{:<6}'.format("[Debug]"), s
        sys.stdout.flush()


def logInfo(s):
    if _logLevel <= WARNING:
        print '{:<6}'.format("[Info]"), s
        sys.stdout.flush()


def logWarn(s):
    if _logLevel <= ERROR:
        print '{:<6}'.format("[Warn]"), s
        sys.stdout.flush()


def logErr(s):
    if _logLevel <= NONE:
        print '{:<6}'.format("[Err]"), s
        sys.stdout.flush()
