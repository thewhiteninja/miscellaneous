from modules.utils import *

PE_MAGIC = 0x5a4d


def Rva2Off(sections, rva):
    for section in sections:
        if section.VirtualAddress <= rva < section.VirtualAddress + section.VirtualSize:
            return rva - section.VirtualAddress + section.PointerToRawData
    return -1


IMAGE_DIRECTORY_ENTRY_EXPORT = 0
IMAGE_DIRECTORY_ENTRY_IMPORT = 1
IMAGE_DIRECTORY_ENTRY_RESOURCE = 2
IMAGE_DIRECTORY_ENTRY_EXCEPTION = 3
IMAGE_DIRECTORY_ENTRY_SECURITY = 4
IMAGE_DIRECTORY_ENTRY_BASERELOC = 5
IMAGE_DIRECTORY_ENTRY_DEBUG = 6
IMAGE_DIRECTORY_ENTRY_COPYRIGHT = 7
IMAGE_DIRECTORY_ENTRY_ARCHITECTURE = 7
IMAGE_DIRECTORY_ENTRY_GLOBALPTR = 8
IMAGE_DIRECTORY_ENTRY_TLS = 9
IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG = 10
IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT = 11
IMAGE_DIRECTORY_ENTRY_IAT = 12
IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT = 13
IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR = 14
IMAGE_DIRECTORY_ENTRY_DOTNET = 15

IMAGE_ORDINAL_FLAG = 0x80000000


class DOSHeader(object):

    def __init__(self, stream):
        self.e_magic = read(stream, 'H')
        self.e_cblp = read(stream, 'H', 2)
        self.e_cp = read(stream, 'H', 4)
        self.e_crlc = read(stream, 'H', 6)
        self.e_cparhdr = read(stream, 'H', 8)
        self.e_minalloc = read(stream, 'H', 10)
        self.e_maxalloc = read(stream, 'H', 12)
        self.e_ss = read(stream, 'H', 14)
        self.e_sp = read(stream, 'H', 16)
        self.e_csum = read(stream, 'H', 18)
        self.e_ip = read(stream, 'H', 20)
        self.e_cs = read(stream, 'H', 22)
        self.e_lfarlc = read(stream, 'H', 24)
        self.e_ovno = read(stream, 'H', 26)
        self.e_res = readArray(stream, 'H', 4, 28)
        self.e_oemid = read(stream, 'H', 36)
        self.e_oeminfo = read(stream, 'H', 38)
        self.e_res2 = readArray(stream, 'H', 10, 40)
        self.e_lfanew = read(stream, 'L', 60)


class RichData(object):

    def __init__(self, compid, times):
        self.id = compid >> 16
        self.version = compid & 0xffff
        self.times = times


class RichStub(object):

    def __init__(self, stream, start, end):
        data = stream[start:end].tobytes()
        self.items = []
        richMarkerPos = data.find("Rich")
        if richMarkerPos != -1:
            richkey = read(stream, "L", start + richMarkerPos + 4)
            if xor(read(stream, "L", start), richkey) == 0x536e6144:  # DanS
                for j in range(16, richMarkerPos, 8):
                    compid = xor(read(stream, "L", start + j), richkey)
                    times = xor(read(stream, "L", start + j + 4), richkey)
                    self.items.append(RichData(compid, times))


class DOSStub(object):

    def __init__(self, stream, start, end):
        data = stream[start:end].tobytes()
        self.data = None
        richMarkerPos = data.find("Rich")
        self.richStubExists = richMarkerPos != -1
        if self.richStubExists:
            richkey = read(stream, "L", start + richMarkerPos + 4)
            for i in range(57, len(data)):
                if xor(read(stream, "L", start + i), richkey) == 0x536e6144:  # DanS
                    self.data = data[:i]
                    break
        else:
            self.data = data

    def isClassicalMessage(self):
        stub = \
            "0E1FBA0E00B409CD21B8014CCD21546869732070726F6772616D2063616E6E6F742062652072756E20696E20444F53206D6F64652E0D0D0A24".decode(
                "hex")
        return self.data == stub + "\x00" * (len(self.data) - len(stub))


class FileHeader(object):

    def __init__(self, stream, offset):
        self.Machine = read(stream, 'H', offset)
        self.NumberOfSections = read(stream, 'H', offset + 2)
        self.TimeDateStamp = read(stream, 'L', offset + 4)
        self.PointerToSymbolTable = read(stream, 'L', offset + 8)
        self.NumberOfSymbols = read(stream, 'L', offset + 12)
        self.SizeOfOptionalHeader = read(stream, 'H', offset + 16)
        self.Characteristics = read(stream, 'H', offset + 18)


class DataDirectory(object):

    def __init__(self, stream, offset):
        self._VirtualAddress = read(stream, "L", offset)
        self._Size = read(stream, "L", offset + 4)


class ExportedFunction(object):

    def __init__(self):
        self.address = 0
        self.name = None
        self.ordinal = 0


class ExportDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ExportDirectory, self).__init__(stream, offset)
        if self._VirtualAddress != 0 and self._Size != 0:
            physAddress = Rva2Off(sections, self._VirtualAddress)
            self.Characteristics = read(stream, 'L', physAddress)
            self.TimeDateStamp = read(stream, 'L', physAddress + 4)
            self.MajorVersion = read(stream, 'H', physAddress + 8)
            self.MinorVersion = read(stream, 'H', physAddress + 10)
            self.Name = read(stream, 'L', physAddress + 12)
            self.Base = read(stream, 'L', physAddress + 16)
            self.NumberOfFunctions = read(stream, 'L', physAddress + 20)
            self.NumberOfNames = read(stream, 'L', physAddress + 24)
            self.AddressOfFunctions = read(stream, 'L', physAddress + 28)
            self.AddressOfNames = read(stream, 'L', physAddress + 32)
            self.AddressOfNameOrdinals = read(stream, 'L', physAddress + 36)
            tmpAddress = Rva2Off(sections, self.AddressOfFunctions)
            tmpAddressNames = Rva2Off(sections, self.AddressOfNames)
            tmpAddressNameOrdinals = Rva2Off(
                sections, self.AddressOfNameOrdinals)
            self.functions = []
            for i in range(self.NumberOfFunctions):
                f = ExportedFunction()
                f.ordinal = read(stream, "H", tmpAddressNameOrdinals + i * 2)
                f.address = read(stream, "L", tmpAddress + f.ordinal * 4)
                f.name = readNullString(stream, Rva2Off(
                    sections, read(stream, "L", tmpAddressNames + i * 4)), 4096)
                self.functions.append(f)


class ImportedFunction(object):

    def __init__(self):
        self.name = None
        self.hint = 0
        self.rva = 0


class ImportDescriptor(object):

    def __init__(self, stream, offset, sections):
        self.OriginalFirstThunk = read(stream, 'L', offset)
        self.Characteristics = self.OriginalFirstThunk
        self.TimeDateStamp = read(stream, 'L', offset + 4)
        self.ForwarderChain = read(stream, 'L', offset + 8)
        self.Name = read(stream, 'L', offset + 12)
        self.FirstThunk = read(stream, 'L', offset + 16)
        if not self.isZeroed():
            self.Name = readNullString(
                stream, Rva2Off(sections, self.Name), 4096)
            self.functions = []
            thunkRVA = self.FirstThunk if self.OriginalFirstThunk == 0 else self.OriginalFirstThunk
            thunk = Rva2Off(sections, thunkRVA)
            thunkDataRVA = read(stream, "L", thunk)
            while thunkDataRVA != 0:
                imf = ImportedFunction()
                imf.rva = thunkDataRVA
                if thunkDataRVA & IMAGE_ORDINAL_FLAG:
                    imf.hint = thunkDataRVA & 0x7fffffff
                else:
                    imf.hint = read(stream, "H", Rva2Off(
                        sections, thunkDataRVA))
                    imf.name = readNullString(stream, Rva2Off(
                        sections, thunkDataRVA) + 2, 4096)
                self.functions.append(imf)
                thunk += 4
                thunkDataRVA = read(stream, "L", thunk)

    def isZeroed(self):
        return self.OriginalFirstThunk == 0 and self.Characteristics == 0 and self.TimeDateStamp == 0 and \
            self.ForwarderChain == 0 and self.Name == 0 and self.FirstThunk == 0


class ImportDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ImportDirectory, self).__init__(stream, offset)
        if self._VirtualAddress != 0 and self._Size != 0:
            physAddress = Rva2Off(sections, self._VirtualAddress)
            self.ImportDescriptors = []
            tmpOffset = 0
            impdesc = ImportDescriptor(
                stream, physAddress + 20 * tmpOffset, sections)
            while not impdesc.isZeroed():
                self.ImportDescriptors.append(impdesc)
                tmpOffset += 1
                impdesc = ImportDescriptor(
                    stream, physAddress + 20 * tmpOffset, sections)


class ResourceDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ResourceDirectory, self).__init__(stream, offset)


class ExceptionDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ExceptionDirectory, self).__init__(stream, offset)


class SecurityDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(SecurityDirectory, self).__init__(stream, offset)
        if self._VirtualAddress != 0 and self._Size != 0:
            self.sigSize = read(stream, "L", self._VirtualAddress)
            self.revision = read(stream, "H", self._VirtualAddress + 4)
            self.certificateType = read(stream, "H", self._VirtualAddress + 6)
            self.signatureDER = stream[
                self._VirtualAddress + 8:self._VirtualAddress + self.sigSize]

            #cert = decoder.decode(self.signatureDER, asn1Spec = pypattern)[0]

            # print cert.getComponentByName("signerInfos")


class RelocationDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(RelocationDirectory, self).__init__(stream, offset)


class DebugDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(DebugDirectory, self).__init__(stream, offset)


class CopyrightDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(CopyrightDirectory, self).__init__(stream, offset)


class ArchitectureDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ArchitectureDirectory, self).__init__(stream, offset)


class GlobalPtrDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(GlobalPtrDirectory, self).__init__(stream, offset)


class TLSDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(TLSDirectory, self).__init__(stream, offset)


class LoadConfigDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(LoadConfigDirectory, self).__init__(stream, offset)


class BoundImportDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(BoundImportDirectory, self).__init__(stream, offset)


class IATDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(IATDirectory, self).__init__(stream, offset)


class DelayImportDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(DelayImportDirectory, self).__init__(stream, offset)


class ComDescriptorDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ComDescriptorDirectory, self).__init__(stream, offset)


class ReservedDirectory(DataDirectory):

    def __init__(self, stream, offset, sections):
        super(ReservedDirectory, self).__init__(stream, offset)


DIRECTORIES = [
    ExportDirectory,
    ImportDirectory,
    ResourceDirectory,
    ExceptionDirectory,
    SecurityDirectory,
    RelocationDirectory,
    DebugDirectory,
    CopyrightDirectory,
    ArchitectureDirectory,
    GlobalPtrDirectory,
    TLSDirectory,
    LoadConfigDirectory,
    BoundImportDirectory,
    IATDirectory,
    DelayImportDirectory,
    ComDescriptorDirectory,
    ReservedDirectory]


class OptionalHeader(object):

    def __init__(self, stream, offset):
        self.Magic = read(stream, 'H', offset)
        self.MajorLinkerVersion = read(stream, 'B', offset + 2)
        self.MinorLinkerVersion = read(stream, 'B', offset + 3)
        self.SizeOfCode = read(stream, 'L', offset + 4)
        self.SizeOfInitializedData = read(stream, 'L', offset + 8)
        self.SizeOfUninitializedData = read(stream, 'L', offset + 12)
        self.AddressOfEntryPoint = read(stream, 'L', offset + 16)
        self.BaseOfCode = read(stream, 'L', offset + 20)
        self.BaseOfData = read(stream, 'L', offset + 24)
        self.ImageBase = read(stream, 'L', offset + 28)
        self.SectionAlignment = read(stream, 'L', offset + 32)
        self.FileAlignment = read(stream, 'L', offset + 36)
        self.MajorOperatingSystemVersion = read(stream, 'H', offset + 40)
        self.MinorOperatingSystemVersion = read(stream, 'H', offset + 42)
        self.MajorImageVersion = read(stream, 'H', offset + 44)
        self.MinorImageVersion = read(stream, 'H', offset + 46)
        self.MajorSubsystemVersion = read(stream, 'H', offset + 48)
        self.MinorSubsystemVersion = read(stream, 'H', offset + 50)
        self.Win32VersionValue = read(stream, 'L', offset + 52)
        self.SizeOfImage = read(stream, 'L', offset + 56)
        self.SizeOfHeaders = read(stream, 'L', offset + 60)
        self.CheckSum = read(stream, 'L', offset + 64)
        self.Subsystem = read(stream, 'H', offset + 68)
        self.DllCharacteristics = read(stream, 'H', offset + 70)
        self.SizeOfStackReserve = read(stream, 'L', offset + 72)
        self.SizeOfStackCommit = read(stream, 'L', offset + 76)
        self.SizeOfHeapReserve = read(stream, 'L', offset + 80)
        self.SizeOfHeapCommit = read(stream, 'L', offset + 84)
        self.LoaderFlags = read(stream, 'L', offset + 88)
        self.NumberOfRvaAndSizes = read(stream, 'L', offset + 92)
        self.DataDirectory = offset + 96


class PEHeader(object):

    def __init__(self, stream, offset):
        self.Signature = read(stream, "L", offset)
        self.FileHeader = FileHeader(stream, offset + 4)
        self.Optionalheader = OptionalHeader(stream, offset + 24)


class Section(object):

    def __init__(self, stream, offset):
        self.Name = readNullString(stream, offset, 8)
        self.PhysicalAddress = read(stream, 'L', offset + 8)
        self.VirtualSize = read(stream, 'L', offset + 8)
        self.VirtualAddress = read(stream, 'L', offset + 12)
        self.SizeOfRawData = read(stream, 'L', offset + 16)
        self.PointerToRawData = read(stream, 'L', offset + 20)
        self.PointerToRelocations = read(stream, 'L', offset + 24)
        self.PointerToLinenumbers = read(stream, 'L', offset + 28)
        self.NumberOfRelocations = read(stream, 'H', offset + 32)
        self.NumberOfLinenumbers = read(stream, 'H', offset + 34)
        self.Characteristics = read(stream, 'L', offset + 36)
        self.data = stream[
            self.PointerToRawData:self.PointerToRawData + self.SizeOfRawData].tobytes()

    def isExecutable(self):
        return self.Characteristics & IMAGE_SCN_MEM_EXECUTE

    def isReadable(self):
        return self.Characteristics & IMAGE_SCN_MEM_READ


class PE(object):

    def __init__(self, filename):
        self.__file = open(filename, "rb")
        self.__stream = memoryview(self.__file.read())
        if self.__file is None:
            self.__file.close()

        self.dos_header = DOSHeader(self.__stream)
        self.dos_stub = DOSStub(self.__stream, 0x40, self.dos_header.e_lfanew)
        self.rich_stub = RichStub(self.__stream, 0x40 + len(self.dos_stub.data), self.dos_header.e_lfanew) if \
            self.dos_stub.richStubExists else None
        self.pe_header = PEHeader(self.__stream, self.dos_header.e_lfanew)
        self.sections = []
        for i in range(self.pe_header.FileHeader.NumberOfSections):
            self.sections.append(Section(self.__stream, self.dos_header.e_lfanew + 24 +
                                         self.pe_header.FileHeader.SizeOfOptionalHeader + (40 * i)))
        dataDirectoryOffset = self.pe_header.Optionalheader.DataDirectory
        self.pe_header.Optionalheader.DataDirectory = []
        for i in range(self.pe_header.Optionalheader.NumberOfRvaAndSizes):
            self.pe_header.Optionalheader.DataDirectory.append(
                DIRECTORIES[i](self.__stream, dataDirectoryOffset + 8 * i,
                               self.sections))

        self.hashs = hashMem(self.__stream)

    def isMagicOK(self):
        return self.dos_header.e_magic == PE_MAGIC

    def isValid(self):
        return True

    def isSuspicious(self):
        return True

    def isPacked(self):
        return True

    def getSectionByName(self, name):
        for section in self.sections:
            if section.Name == name:
                return section
        return None

    def computeRichKey(self):
        if self.rich_stub is None:
            logger.logWarn("There is no rich stub in the executable")
            return -1
        chksum = 0x40 + len(self.dos_stub.data)
        for i in range(0x40 + len(self.dos_stub.data) - 4):
            chksum += rol32(ord(self.__stream[i]), i)
        for i in self.rich_stub.items:
            compid = i.id << 16 | i.version
            chksum += rol32(compid, i.times)
        return chksum & 0xffffffff
