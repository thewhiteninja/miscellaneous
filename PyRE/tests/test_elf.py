import unittest

from modules.linux.ELF import *

testCaseName = "ELF"
testCaseDesc = "Testing ELF parser"
testCaseClassName = "TestELF"


class TestELF(unittest.TestCase):
    e = None

    @classmethod
    def setUpClass(cls):
        cls.e = ELF("tests/data/elf32")
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_magic(self):
        self.assertTrue(self.e.isMagicOK(), "Bad magic number")


if __name__ == '__main__':
    print "Please run test.py in the parent folder"
