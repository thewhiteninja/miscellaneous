import unittest

from modules.windows.PE import *

testCaseName = "PE"
testCaseDesc = "Testing PE parser"
testCaseClassName = "TestPE"


class TestPE(unittest.TestCase):
    e = None

    @classmethod
    def setUpClass(cls):
        cls.e = PE("tests/data/ok.exe")
        cls.e2 = PE("tests/data/MSCOMCTL.OCX")
        cls.e3 = PE("tests/data/HelpPane.exe")

    @classmethod
    def tearDownClass(cls):
        pass

    def test_magic(self):
        self.assertTrue(self.e.isMagicOK(), "Bad magic number")

    def test_RichHeader(self):
        self.assertEqual(self.e3.dos_stub.richStubExists, True)
        self.assertEqual(len(self.e3.rich_stub.items), 8)
        self.assertEqual(self.e3.rich_stub.items[0].id, 205)
        self.assertEqual(self.e3.rich_stub.items[0].version, 65501)
        self.assertEqual(self.e3.rich_stub.items[0].times, 4)
        self.assertEqual(self.e3.rich_stub.items[3].id, 1)
        self.assertEqual(self.e3.rich_stub.items[3].version, 0)
        self.assertEqual(self.e3.rich_stub.items[3].times, 345)
        self.assertEqual(self.e3.rich_stub.items[7].id, 204)
        self.assertEqual(self.e3.rich_stub.items[7].version, 65501)
        self.assertEqual(self.e3.rich_stub.items[7].times, 1)
        # TODO fix
        self.assertEqual(self.e3.computeRichKey(), 3133836124)

    def test_DosHeader(self):
        self.assertEqual(self.e.dos_header.e_magic, 0x5a4d)
        self.assertEqual(self.e.dos_header.e_cblp, 0x90)
        self.assertEqual(self.e.dos_header.e_cp, 0x3)
        self.assertEqual(self.e.dos_header.e_cparhdr, 0x4)
        self.assertEqual(self.e.dos_header.e_crlc, 0x0)
        self.assertEqual(self.e.dos_header.e_cs, 0x0)
        self.assertEqual(self.e.dos_header.e_csum, 0x0)
        self.assertEqual(self.e.dos_header.e_ip, 0x0)
        self.assertEqual(self.e.dos_header.e_lfanew, 0x80)
        self.assertEqual(self.e.dos_header.e_lfarlc, 0x40)
        self.assertEqual(self.e.dos_header.e_maxalloc, 0xffff)
        self.assertEqual(self.e.dos_header.e_minalloc, 0x0)
        self.assertEqual(self.e.dos_header.e_oemid, 0x0)
        self.assertEqual(self.e.dos_header.e_oeminfo, 0x0)
        self.assertEqual(self.e.dos_header.e_ovno, 0x0)
        self.assertEqual(self.e.dos_header.e_res, [0, 0, 0, 0])
        self.assertEqual(self.e.dos_header.e_res2, [
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(self.e.dos_header.e_sp, 0xb8)
        self.assertEqual(self.e.dos_header.e_ss, 0x0)

    def test_FileHeader(self):
        self.assertEqual(self.e.pe_header.Signature, 0x4550)
        self.assertEqual(self.e.pe_header.FileHeader.Characteristics, 0x107)
        self.assertEqual(self.e.pe_header.FileHeader.Machine, 0x14c)
        self.assertEqual(self.e.pe_header.FileHeader.NumberOfSections, 0xf)
        self.assertEqual(self.e.pe_header.FileHeader.NumberOfSymbols, 0x4ed)
        self.assertEqual(
            self.e.pe_header.FileHeader.PointerToSymbolTable, 0x12800)
        self.assertEqual(
            self.e.pe_header.FileHeader.SizeOfOptionalHeader, 0xe0)
        self.assertEqual(self.e.pe_header.FileHeader.TimeDateStamp, 0x5304b698)

    def test_OptionalHeader(self):
        self.assertEqual(
            self.e.pe_header.Optionalheader.AddressOfEntryPoint, 0x1500)
        self.assertEqual(self.e.pe_header.Optionalheader.BaseOfCode, 0x1000)
        self.assertEqual(self.e.pe_header.Optionalheader.BaseOfData, 0x3000)
        self.assertEqual(self.e.pe_header.Optionalheader.CheckSum, 0x28630)

        self.assertEqual(
            self.e.pe_header.Optionalheader.DllCharacteristics, 0x0)
        self.assertEqual(self.e.pe_header.Optionalheader.FileAlignment, 0x200)
        self.assertEqual(self.e.pe_header.Optionalheader.ImageBase, 0x400000)
        self.assertEqual(self.e.pe_header.Optionalheader.LoaderFlags, 0x0)
        self.assertEqual(self.e.pe_header.Optionalheader.Magic, 0x10b)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MajorImageVersion, 0x1)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MajorLinkerVersion, 0x2)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MajorOperatingSystemVersion, 0x4)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MajorSubsystemVersion, 0x4)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MinorImageVersion, 0x0)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MinorLinkerVersion, 0x17)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MinorOperatingSystemVersion, 0x0)
        self.assertEqual(
            self.e.pe_header.Optionalheader.MinorSubsystemVersion, 0x0)
        self.assertEqual(
            self.e.pe_header.Optionalheader.NumberOfRvaAndSizes, 0x10)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SectionAlignment, 0x1000)
        self.assertEqual(self.e.pe_header.Optionalheader.SizeOfCode, 0x1800)
        self.assertEqual(self.e.pe_header.Optionalheader.SizeOfHeaders, 0x400)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfHeapCommit, 0x1000)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfHeapReserve, 0x100000)
        self.assertEqual(self.e.pe_header.Optionalheader.SizeOfImage, 0x1d000)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfInitializedData, 0x1200)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfStackCommit, 0x1000)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfStackReserve, 0x200000)
        self.assertEqual(
            self.e.pe_header.Optionalheader.SizeOfUninitializedData, 0x400)
        self.assertEqual(self.e.pe_header.Optionalheader.Subsystem, 0x3)
        self.assertEqual(
            self.e.pe_header.Optionalheader.Win32VersionValue, 0x0)

    def test_Sections(self):
        self.assertEqual(len(self.e.sections), 0xf)
        self.assertEqual(self.e.sections[0].Name, ".text")
        self.assertEqual(self.e.sections[0].PhysicalAddress, 0x1788)
        self.assertEqual(self.e.sections[0].VirtualSize, 0x1788)
        self.assertEqual(self.e.sections[0].VirtualAddress, 0x1000)
        self.assertEqual(self.e.sections[0].SizeOfRawData, 0x1800)
        self.assertEqual(self.e.sections[0].PointerToRawData, 0x400)
        self.assertEqual(self.e.sections[0].PointerToRelocations, 0x0)
        self.assertEqual(self.e.sections[0].PointerToLinenumbers, 0x0)
        self.assertEqual(self.e.sections[0].NumberOfRelocations, 0x0)
        self.assertEqual(self.e.sections[0].NumberOfLinenumbers, 0x0)
        self.assertEqual(self.e.sections[0].Characteristics, 0x60500020)

    def test_Directory(self):
        self.assertEqual(
            self.e.pe_header.Optionalheader.NumberOfRvaAndSizes, 0x10)
        self.assertEqual(self.e.pe_header.Optionalheader.DataDirectory[
                         0]._VirtualAddress, 0)
        self.assertEqual(
            self.e.pe_header.Optionalheader.DataDirectory[0]._Size, 0)
        self.assertEqual(self.e.pe_header.Optionalheader.DataDirectory[
                         1]._VirtualAddress, 0x6000)
        self.assertEqual(
            self.e.pe_header.Optionalheader.DataDirectory[1]._Size, 0x59c)
        self.assertEqual(self.e.pe_header.Optionalheader.DataDirectory[
                         0xf]._VirtualAddress, 0)
        self.assertEqual(
            self.e.pe_header.Optionalheader.DataDirectory[0xf]._Size, 0)

    def test_Import(self):
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT]._VirtualAddress, 0xab840)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_IMPORT]._Size, 0xf8)
        self.assertEqual(len(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors), 0x7)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[0].Name, "KERNEL32.dll")
        self.assertEqual(len(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[0].functions), 103)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[6].Name, "GDI32.dll")
        self.assertEqual(len(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[6].functions), 78)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[5].functions[0].name, "GetOpenFileNameA")
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[5].functions[0].hint, 0x9)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_IMPORT].ImportDescriptors[5].functions[0].rva, 0xad390)

    def test_Export(self):
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_EXPORT]._VirtualAddress, 0x64400)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_EXPORT]._Size, 0xc3)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].Characteristics,
                         0x0)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].TimeDateStamp,
                         0x4186a0c7)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_EXPORT].MajorVersion, 0x0)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_EXPORT].MinorVersion, 0x0)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_EXPORT].Name, 0x6445a)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
                         IMAGE_DIRECTORY_ENTRY_EXPORT].Base, 0x1)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_EXPORT].NumberOfFunctions, 0x5)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].NumberOfNames,
                         0x5)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_EXPORT].AddressOfFunctions, 0x64428)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_EXPORT].AddressOfNames, 0x6443c)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[
            IMAGE_DIRECTORY_ENTRY_EXPORT].AddressOfNameOrdinals, 0x64450)
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[0].ordinal, 4)
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[0].address, 0x6658A)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[0].name,
                         "DLLGetDocumentation")
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[1].ordinal, 0)
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[1].address, 0x160e8)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[1].name,
                         "DllCanUnloadNow")
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[4].ordinal, 3)
        self.assertEqual(
            self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[4].address, 0x080038)
        self.assertEqual(self.e2.pe_header.Optionalheader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].functions[4].name,
                         "DllUnregisterServer")


if __name__ == '__main__':
    print "Please run test.py in the parent folder"
