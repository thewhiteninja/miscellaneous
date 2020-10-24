import base
import pprint
from capstone import *
from modules import logger
from modules import database
from modules.windows.PE import *

pluginMainClass = "ROP"

STOP_INSTRS = ["je", "insb", "insd", "insw", "jne"]
GO_INSTRS = ["call", "ret", "retn"]

md = None


class Gadget(object):

    def __init__(self, address, instrs=[]):
        self.address = address
        self.instrs = []

    def add(self, instr):
        self.instrs.insert(0, instr)

    def __repr__(self):
        return "; ".join(self.instrs)


class ROP(base.Plugins):

    def __init__(self):
        super(ROP, self).__init__()
        self.name = "ROPfu"
        self.version = "1.0.0.0"
        self.descriptionShort = "Gadget finder and ROPchain builder for Pyre."
        self.description = "Gadget finder and ROPchain builder for Pyre."
        self.help = \
            """    find_gadget
                    maxlen 3  : Maximum number of instruction before ret
                    nonull    : Skip gadget at address containing a null byte
                    utf7      : Skip gadget at address containing a byte > 127    """
        self.db_model = \
            """CREATE TABLE results (id INT, my_var1 TEXT, my_var2 TEXT)"""
        self.db = database.create(":memory:", self.db_model)
        self.handler = None

    def call(self, handler, params):
        if not handler.dbg.loaded:
            logger.logErr("No executable loaded")
            return
        cmd = params[0]
        if cmd == "f":
            maxlen = 3
            nonull = False
            utf7 = False
            i = 0
            end = len(params)
            while i < end:
                if params[i] == "maxlen":
                    if i + 1 < end:
                        if params[i + 1].isdigit():
                            maxlen = params[i + 1]
                            i += 1
                        else:
                            logger.logErr(
                                "No integer value provided for parameter maxlen")
                            return
                    else:
                        logger.logErr("No value provided for parameter maxlen")
                        return
                elif params[i] == "nonull":
                    nonull = True
                elif params[i] == "utf8":
                    utf7 = True
                i += 1
            self.findGadget(handler, maxlen, nonull, utf7)
        else:
            logger.logInfo("No command named %s for this plugin" % cmd)

    def __del__(self):
        self.db.commit()
        self.db.close()

    def __next_gadget(self, data, start):
        global md
        RET1 = "\xc3"
        RET2 = "\xc2"
        CALL1 = "\xe8"
        CALL2 = "\xff"
        addr = min(data.find(RET1, start), data.find(RET2, start),
                   data.find(CALL1, start), data.find(CALL2, start))
        return addr

    def findGadget(self, handler, maxlen, nonull, utf7):
        global md
        gadgets = dict()
        e = handler.dbg.executable
        md = Cs(CS_ARCH_X86, CS_MODE_32)
        ImageBase = e.pe_header.Optionalheader.ImageBase
        for section in e.sections:
            if section.isExecutable():
                logger.logInfo("Searching gadget in %s section (%d bytes)" % (section.Name,
                                                                              section.SizeOfRawData))
                for i in range(0, 5):
                    instrs = list(md.disasm_lite(
                        section.data[i:], ImageBase + section.VirtualAddress))[::-1]
                    idx = 0
                    while idx < len(instrs):
                        (address, size, mnemonic, op_str) = instrs[idx]
                        if mnemonic == "ret":
                            add = True
                            g = Gadget(address)
                            #for o in range(maxlen):
                                #         if instr[2] not in STOP_INSTRS:
                                #             g.add(instr[2] + " " + instr[3])
                                #         else:
                                #             add = False
                                #             break
                                #     if add:
                                #         if gadgets.has_key(repr(g)):
                                #             gadgets[repr(g)].append("0x%08x"%g.address)
                                #         else:
                                #             gadgets[repr(g)] = ["0x%08x"%g.address]
                                #
                        if hasNull(g.address) and nonull:
                            continue
                        if hasUTF8(g.address) and utf7:
                            continue
        pprint.pprint(gadgets)
        print len(gadgets)
