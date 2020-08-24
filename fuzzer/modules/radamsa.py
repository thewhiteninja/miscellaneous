import os
import subprocess


def generateMutant(f, n, d):
    exec_radamsa = " ".join(["radamsa", '-o', os.path.join(d, os.path.basename(f) + "_%n"), '-n', str(n), f])
    p = subprocess.Popen(exec_radamsa)
    p.wait()
