from modules import logger

BP_HW_EXEC, BP_HW_WRITE, BP_HW_RESERVED, BP_HW_READORWRITE = 0, 1, 2, 3
BP_HW_LEN_1, BP_HW_LEN_2, BP_HW_LEN_4 = 0, 1, 3
BP_READ, BP_WRITE, BP_EXEC = 4, 2, 1
BP_TYPE_SOFTWARE, BP_TYPE_HARDWARE, BP_TYPE_MEMORY = 0, 1, 2
DR0, DR1, DR2, DR3 = 0, 1, 2, 3


class DebuggerBreakpoint:

    def __init__(self):
        self.__backup = None
        self.address = -1
        self.condition = None
        self.handler = None
        self.access = -1
        self.size = -1
        self.register = -1
        self.type = -1

    def __repr__(self):
        return "%s breakpoint at %08x %s" % (
            ["Software", "Memory", "Hardware"][self.type], self.address, "[handler -> " + self.handler.__name__ if
            self.handler is not None else "")


class DebuggerBreakpoints:

    def __init__(self):
        self.__hw_bp_avail_regs = [DR0, DR1, DR2, DR3]
        self.__breakpoints = dict()

    def add(self, address, handler=None, condition=None):
        return self.add_sw(address, handler, condition)

    def add_sw(self, address, handler=None, condition=None):
        if not self.is_breakpointed(address):
            bp = DebuggerBreakpoint()
            bp.type = BP_TYPE_SOFTWARE
            bp.handler = handler
            bp.address = address
            bp.condition = condition
            self.__breakpoints[address] = bp
            return bp
        else:
            logger.logWarn(
                "Software breakpoint already exists at address 0x%08x" % address)
            return None

    def add_mem(self, address, handler=None, condition=None, access=0):
        if not self.is_breakpointed(address):
            if 0 < access <= 7:
                bp = DebuggerBreakpoint()
                bp.type = BP_TYPE_MEMORY
                bp.address = address
                bp.handler = handler
                bp.condition = condition
                bp.access = access
                self.__breakpoints[address] = bp
                return bp
            else:
                logger.logWarn("Memory breakpoint access has to be a combination of BP_READ, BP_WRITE, "
                               "BP_EXEC")
        else:
            logger.logWarn(
                "Memory breakpoint already exists at address 0x%08x" % address)
        return None

    def add_hw(self, address, handler=None, condition=None, access=BP_EXEC, size=4):
        if not self.is_breakpointed(address):
            if len(self.__hw_bp_avail_regs) > 0:
                if access in [BP_HW_EXEC, BP_HW_WRITE, BP_HW_READORWRITE]:
                    if size in [BP_HW_LEN_1, BP_HW_LEN_2, BP_HW_LEN_4]:
                        bp = DebuggerBreakpoint()
                        bp.type = BP_TYPE_HARDWARE
                        bp.address = address
                        bp.handler = handler
                        bp.condition = condition
                        bp.access = access
                        bp.size = size
                        bp.register = self.__hw_bp_avail_regs.pop(0)
                        self.__breakpoints[address] = bp
                        return bp
                    else:
                        logger.logWarn(
                            "Hardware breakpoint size has to be BP_HW_LEN_1, BP_HW_LEN_2 or BP_HW_LEN_4")
                else:
                    logger.logWarn(
                        "Hardware breakpoint access has to be BP_HW_EXEC, BP_HW_WRITE or BP_HW_READORWRITE")
            else:
                logger.logWarn("Maximum hardware breakpoints reached (4)")
        else:
            logger.logWarn(
                "Hardware breakpoint already exists at address %08x" % address)
        return None

    def get_all(self):
        return self.__breakpoints.keys()

    def is_breakpointed(self, addr):
        return addr in self.__breakpoints.keys()

    def get(self, address):
        if self.__breakpoints.has_key(address):
            return self.__breakpoints[address]
        return None

    def remove(self, address):
        if self.__breakpoints.has_key(address):
            return self.__breakpoints.pop(address)
        return None

    def remove_all(self):
        tmp = self.__breakpoints.values()
        self.__breakpoints.clear()
        return tmp

    def count(self):
        return len(self.__breakpoints)
