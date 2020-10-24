import os
import sys
import platform
import importlib

from modules import utils
from modules import interactive_mode
from modules import logger
from modules import database

args = utils.Args()


def parse_args(a):
    global args
    i = 1
    while i < len(a):
        if a[i][0] == "-":
            usage()
        else:
            args.executable_filename = a[i]
        i += 1


def getPlugins():
    plugins = dict()
    rootDir = os.getcwd() + os.sep + "plugins"
    for fname in os.listdir(rootDir):
        if not fname.startswith("base") and not fname.startswith("__") and fname.endswith(".py"):
            fname = os.path.join("plugins", fname).replace(os.sep, ".")[:-3]
            mod = importlib.import_module(fname)
            if mod:
                inst = getattr(mod, getattr(mod, "pluginMainClass"))()
                logger.logDebug("Plugin %s v%s loaded" %
                                (inst.name, inst.version))
                plugins[inst.name] = inst
    return plugins


def init():
    curdir = os.getcwd()
    if not os.path.exists(os.path.join(curdir, '.tmp')):
        logger.logDebug("Creating tmp folder")
        os.makedirs(os.path.join(curdir, '.tmp'))
    else:
        logger.logDebug("Temp folder created")
    s = platform.platform()
    if s.startswith("Windows"):
        pass
    elif s.startswith("Linux") or s.startswith("Mac"):
        pass
    else:
        logger.logErr(
            "Unable to download required programs four your platform")


def usage():
    print
    print "    Usage: %s [Options] [executable]" % (os.path.basename(sys.argv[0]))
    print
    print "    Options :"
    print "        -h, --help : Help"
    sys.exit(1)


def main():
    utils.welcome()
    logger.logLevel(logger.INFO)
    init()
    if len(sys.argv) > 1:
        parse_args(sys.argv)
    plugins = getPlugins()
    h = interactive_mode.CmdHandler(args, plugins)
    while 1:
        try:
            h.cmdloop()
        except KeyboardInterrupt:
            print
            pass
    for p in plugins:
        del p

if __name__ == "__main__":
    main()
