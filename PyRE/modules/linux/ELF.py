import struct

ELF_MAGIC = "\x7fELF"


class ELFIdent(object):

    def __init__(self, stream):
        self.ei_magic = stream[0:4].tobytes()
        self.ei_class = struct.unpack('<B', stream[4:5].tobytes())[0]
        self.ei_data = struct.unpack('<B', stream[5:6].tobytes())[0]
        self.ei_version = struct.unpack('<B', stream[6:7].tobytes())[0]
        self.ei_osabi = struct.unpack('<B', stream[7:8].tobytes())[0]
        self.ei_abiversion = struct.unpack('<B', stream[8:9].tobytes())[0]
        self.ei_pad = stream[9:16].tobytes()


class ELFHeader(object):

    def __init__(self, stream):
        self.e_ident = ELFIdent(stream)
        self.e_type = struct.unpack('<H', stream[16:18].tobytes())[0]
        self.e_machine = struct.unpack('<H', stream[18:20].tobytes())[0]
        self.e_version = struct.unpack('<L', stream[20:24].tobytes())[0]
        self.e_entry = struct.unpack('<L', stream[24:28].tobytes())[0]
        self.e_phoff = struct.unpack('<L', stream[28:32].tobytes())[0]
        self.e_shoff = struct.unpack('<L', stream[32:36].tobytes())[0]
        self.e_flags = struct.unpack('<L', stream[36:40].tobytes())[0]
        self.e_ehsize = struct.unpack('<H', stream[40:42].tobytes())[0]
        self.e_phentsize = struct.unpack('<H', stream[42:44].tobytes())[0]
        self.e_phnum = struct.unpack('<H', stream[44:46].tobytes())[0]
        self.e_shentsize = struct.unpack('<H', stream[46:48].tobytes())[0]
        self.e_shnum = struct.unpack('<H', stream[48:50].tobytes())[0]
        self.e_shstrndx = struct.unpack('<H', stream[50:52].tobytes())[0]


class SectionHeader(object):

    def __init__(self, stream, offset):
        self.sh_name = struct.unpack(
            '<L', stream[offset:offset + 4].tobytes())[0]
        self.sh_type = struct.unpack(
            '<L', stream[offset + 4:offset + 8].tobytes())[0]
        self.sh_flags = struct.unpack(
            '<L', stream[offset + 8:offset + 12].tobytes())[0]
        self.sh_addr = struct.unpack(
            '<L', stream[offset + 12:offset + 16].tobytes())[0]
        self.sh_offset = struct.unpack(
            '<L', stream[offset + 16:offset + 20].tobytes())[0]
        self.sh_size = struct.unpack(
            '<L', stream[offset + 20:offset + 24].tobytes())[0]
        self.sh_link = struct.unpack(
            '<L', stream[offset + 24:offset + 28].tobytes())[0]
        self.sh_info = struct.unpack(
            '<L', stream[offset + 28:offset + 32].tobytes())[0]
        self.sh_addralign = struct.unpack(
            '<L', stream[offset + 32:offset + 36].tobytes())[0]
        self.sh_entsize = struct.unpack(
            '<L', stream[offset + 36:offset + 40].tobytes())[0]


class ProgramHeader(object):

    def __init__(self, stream, offset):
        self.p_type = struct.unpack(
            '<L', stream[offset:offset + 4].tobytes())[0]
        self.p_offset = struct.unpack(
            '<L', stream[offset + 4:offset + 8].tobytes())[0]
        self.p_vaddr = struct.unpack(
            '<L', stream[offset + 8:offset + 12].tobytes())[0]
        self.p_paddr = struct.unpack(
            '<L', stream[offset + 12:offset + 16].tobytes())[0]
        self.p_filesz = struct.unpack(
            '<L', stream[offset + 16:offset + 20].tobytes())[0]
        self.p_memsz = struct.unpack(
            '<L', stream[offset + 20:offset + 24].tobytes())[0]
        self.p_flags = struct.unpack(
            '<L', stream[offset + 24:offset + 28].tobytes())[0]
        self.p_align = struct.unpack(
            '<L', stream[offset + 28:offset + 32].tobytes())[0]


class ELF(object):

    def __init__(self, filename):
        self.__file = open(filename, "rb")
        self.__stream = memoryview(self.__file.read())
        if self.__file is None:
            self.__file.close()

        self.header = ELFHeader(self.__stream)
        self.programheaders = []
        for i in range(self.header.e_phnum):
            self.programheaders.append(ProgramHeader(
                self.__stream, self.header.e_phoff + i * self.header.e_phentsize))
        self.sections = []
        for i in range(self.header.e_shnum):
            self.sections.append(SectionHeader(
                self.__stream, self.header.e_shoff + i * self.header.e_shentsize))
        self.__shstrTable = self.__readShStrTable()

    def isMagicOK(self):
        return self.header.e_ident.ei_magic == ELF_MAGIC

    def __readShStrTable(self):
        table = {}
        section = self.sections[self.header.e_shstrndx]
        i = 0
        idx = 0
        name = ""
        while i < section.sh_size:
            if self.__stream[section.sh_offset + i] == "\0":
                table[idx] = name
                name = ""
                idx = i + 1
            else:
                name += self.__stream[section.sh_offset + i]
            i += 1
        return table

    def getStringFromTable(self, idx):
        if self.__shstrTable.has_key(idx):
            return self.__shstrTable[idx]
        else:
            raise Exception("Invalid index for the string table: " + idx)

    def getSectionHeaderByName(self, name):
        nameIdx = self.__shstrTable.values().index(name)
        for s in self.sections:
            if s.sh_name == nameIdx:
                return s
        raise Exception("Invalid name for section: " + name)

    def getSectionNameByAddress(self, address):
        for s in self.sections:
            if s.sh_addr <= address <= s.sh_addr + s.sh_size:
                return self.__shstrTable[s.sh_name]
        raise Exception("Invalid address for section: " + hex(address))

    def __del__(self):
        if self.__file is not None:
            self.__file.close()
