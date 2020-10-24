import time, sys
import subprocess 
from subprocess import *
from itertools import *

keySize = 24

def xor(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))
		
################################################################################

pub = [964266105338945, 6749864515101946, 964264861986975, 13499727318176232, 17356789956975810, 3857053002628327, 12535438500695219, 10606879723866753, 10606828405887831, 16392324024362666, 13499318722439347, 7713307812454905, 6748217527825207, 6746569486347068, 8671806553725916, 2879615947706164, 18294696345811439, 6697131932913639, 15322796985338016, 753333165640954, 16934930158297044, 10727464396496856, 8919464717468072, 12053330796850461]
cipher = set([85665597416613316, 68924182376697138, 93855260302436631, 67069112787809230, 67823425594155918, 96038092151406072, 88581012026674643, 87131275443855194, 92447984720405935, 78684146336120268, 52303820625741832, 85294112192719803, 48802767159478973, 93706609509995531, 143147771785836836, 79544023096864593, 118984178180084169, 66881447736363380, 83048004789685724])

################################################################################

t = time.clock()

def ItoA(b):
	plain = ""
	b = bin(b)[2:]
	b = ("0" * (keySize - len(b))) + b
	for i in range(0, len(b), 8):
		plain += chr(int(b[i:i+8], 2))
	return plain	

def bruteBin(s, n, b):
	if n < keySize:
		bruteBin(s, n+1, b << 1)
		bruteBin(s+pub[n], n+1, (b << 1) | 1)			
	else:
		if s in cipher:
			cipher.remove(s)
			plain = ItoA(b)
			print str(s) + "\t:\t" + plain + " (after " +  "%.3f" % (time.clock()-t) + "s by proc" + sys.argv[2] + ")"

import cProfile
			
if len(sys.argv) == 1:
	print "Usage: " + sys.argv[0] + " nb_procs"
elif len(sys.argv) == 2 and sys.argv[1] in ["1", "2", "4"]:
	procs = []
	for i in range(int(sys.argv[1])):
		procs.append(subprocess.Popen(["python", sys.argv[0], sys.argv[1], str(i)]))
	status = [None]
	while None in status:
		time.sleep(10)
		status = [p.poll() for p in procs]
	print "End of BF (total : " +  "%.3f" % (time.clock()-t) + "s)"
elif len(sys.argv) == 3:
	if sys.argv[1] == "1":
		cProfile.run('bruteBin(0,0,0)')
	elif sys.argv[1] == "2":
		if sys.argv[2] == "0":
			cProfile.run('bruteBin(0,1,0)')
		if sys.argv[2] == "1":
			cProfile.run('bruteBin(pub[0],1,1)')
else:
	print "No no no, check the proc number ..."
	