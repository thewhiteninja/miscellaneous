import glob
import os
import platform
import sys
import time

from modules import commands
from modules import database
from modules import debugger
from modules import logger
from modules import radamsa
from modules import utils


class Args:
    def __init__(self):
        self.command = None
        self.exe = ""
        self.input = ""
        self.inputs = []
        self.nbtests = "10"
        self.timeout = 5

    pass


args = Args()


def run():
    logger.logInfo(args.command)


def parseArgs(a):
    global args
    i = 1
    while i < len(a):
        if not a[i].startswith("-"):
            if a[i] in ["init", "fuzz", "replay", "analyze", "test", "debug"]:
                args.command = a[i]
            else:
                logger.logErr("Unknown command: " + a[i])
                usage()
        else:
            if a[i] in ["-e", "--exe"]:
                args.exe = a[i + 1]
                i += 1
            elif a[i] in ["-i", "--input"]:
                args.input = a[i + 1]
                i += 1
            elif a[i] in ["-t", "--timeout"]:
                args.timeout = int(a[i + 1])
                i += 1
            elif a[i] in ["-n"]:
                args.nbtests = a[i + 1]
                i += 1
        i += 1


def init():
    logger.logStep("Initialization")
    curDir = os.getcwd()
    logger.logInfo("Creating SQLite database")
    if not os.path.exists(os.path.join(curDir, 'database')):
        os.makedirs(os.path.join(curDir, 'database'))
    database.init(os.path.join(curDir, 'database', "fuzzingresults.db"))
    logger.logInfo("Creating crash folder")
    if not os.path.exists(os.path.join(curDir, 'crashes')):
        os.makedirs(os.path.join(curDir, 'crashes'))
    logger.logInfo("Creating tmp folder")
    if not os.path.exists(os.path.join(curDir, 'tmp')):
        os.makedirs(os.path.join(curDir, 'tmp'))
    s = platform.platform()
    if s.startswith("Windows"):
        if not os.path.exists("radamsa.exe"):
            logger.logInfo("Downloading radamsa.exe from http://ouspg.googlecode.com")
            utils.download("http://ouspg.googlecode.com/files/radamsa-0.3.exe", "radamsa.exe")
    elif s.startswith("Linux") or s.startswith("Mac"):
        if not os.path.exists("radamsa"):
            logger.logInfo("Downloading radamsa from http://ouspg.googlecode.com")
            utils.download("http://ouspg.googlecode.com/files/radamsa-0.3", "radamsa")
            os.chmod("radamsa", os.stat.S_IXOTH)
    else:
        logger.logErr("Unable to download radamsa four your platform")


def fuzz():
    global args
    logger.logStep("Fuzzing")
    logger.logInfo("Checking options")
    if not utils.is_executable(args.exe):
        sys.exit(1)
    if not (args.nbtests.isdigit() and 0 < int(args.nbtests) < 10000):
        logger.logErr("Number of tests between 1 and 10000 required")
        sys.exit(1)
    else:
        args.nbtests = int(args.nbtests)
    for f in glob.glob(args.input):
        args.inputs.append(f)
    logger.logInfo(str(len(args.inputs)) + " input files found")
    if len(args.inputs) == 0:
        logger.logErr("At least one input file has to be provided")
        sys.exit(1)
    logger.logStep("Creating folder for the executable")

    crashDir = os.path.join(os.getcwd(), 'crashes', os.path.basename(args.exe) + "_" + utils.sha256(args.exe))
    if not os.path.exists(crashDir):
        os.makedirs(os.path.join(crashDir))

    max_inputs = len(args.inputs)
    for i in range(max_inputs):
        utils.clean_folder('tmp')
        logger.logStep(
            "Generating " + str(args.nbtests) + " mutants for file (" + str(i + 1) + "/" + str(max_inputs) + "): " +
            args.inputs[i])
        radamsa.generateMutant(args.inputs[i], args.nbtests, "tmp")
        for i2 in glob.glob('tmp/*'):
            logger.logInfo("Testing executable: " + i2)
            dbg = debugger.Debugger()
            dbg.options.process_timeout = args.timeout
            dbg.load(args.exe, i2)


def interactive():
    while 1:
        try:
            cmd = input("> ")
            if cmd in ["exit", "q", "quit"]:
                commands.exit()
            elif cmd in { "load", "l" }:
                commands.load()
            else:
                commands.unknown()
        except KeyboardInterrupt:
            commands.exit()


def start():
    if args.command == "init":
        init()
    elif args.command == "fuzz":
        fuzz()
    elif args.command == "replay":
        logger.logWarn("Not yet implemented: " + args.command)
        sys.exit(1)
    elif args.command == "analyze":
        logger.logWarn("Not yet implemented: " + args.command)
        sys.exit(1)
    elif args.command == "test":
        test()
    elif args.command == "debug":
        interactive()
    else:
        usage()


def testcb(bp):
    print(bp)


def test():
    dbg = debugger.Debugger()
    dbg.options.process_timeout = args.timeout
    dbg.load(args.exe, "")
    dbg.set_breakpoint(0x004015A5, testcb)
    dbg.run()


def usage():
    print("usage:", os.path.basename(sys.argv[0]), "command", "[OPTIONS]")
    print()
    print("commands:")
    print("    init           - Create folders and database for the results")
    print("    fuzz           - Start a new fuzzing session")
    print("    replay         - Search in the results")
    print("    analysze       - Delete the results")
    print("    debug          - Start interactive debugger")
    print()
    print("options:")
    print("    -e,--exe       - Executable to fuzz")
    print("    -t,--timeout   - Set the timeout before killing the process")
    print("    -i,--input     - Input files")
    print("    -n             - Number of tests per file")
    print()
    sys.exit(1)


def welcome():
    print("Starting", os.path.basename(sys.argv[0]), "at", time.asctime(time.localtime(time.time())),
          "(" + platform.architecture()[0] + " version)")
    print()


def main():
    welcome()
    if len(sys.argv) > 1:
        parseArgs(sys.argv)
        start()
    else:
        usage()


if __name__ == "__main__":
    main()
