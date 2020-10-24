import time, sys, math, random
from random import randint
from itertools import *

keySize = 24

def gcd(a,b):
	while b != 0:
		a, b = b, a%b
	return a
	
def coprime(a,b):
	return gcd(a,b) == 1
	
def toBin(s):
	b = ""
	for c in s:
		rep = bin(ord(c))[2:]
		b += ("0" * (8 - len(rep))) + rep
	return b

def superIncreasing(r, n):
	seq = []
	rs = 1
	for i in range(n):
		seq += [randint(rs, rs+r)]
		rs += seq[-1]
	return seq
	
def egcd(a,b):
	u, u1 = 1, 0
	v, v1 = 0, 1
	while b:
		q = a // b
		u, u1 = u1, u - q * u1
		v, v1 = v1, v - q * v1
		a, b = b, a - q * b
	return u, v, a

def modInv(e,n):
	return egcd(e,n)[0]%n
	
def enc(text, key):
	ciphered = []
	text += " "*(((keySize/8)-(len(text)%(keySize/8)))%(keySize/8))
	for i in range(0, len(text), keySize/8):
		sum = 0
		b = toBin(text[i:i+(keySize/8)])
		for j in range(keySize):
			sum += int(b[j])*key[j]
		ciphered += [sum]
	return ciphered

def dec(cipher, key):
	priv, w, n = key
	priv = priv[::-1]
	plain = ""
	for c in cipher:
		inv = c * modInv(w, n) % n
		b = ""
		for i in range(keySize):
			if priv[i] <= inv:
				b = "1" + b
				inv -= priv[i]
			else:
				b = "0" + b
		for i in range(0, len(b), 8):
			plain += chr(int(b[i:i+8], 2))
	return plain.strip()
	
def miller_rabin_pass(a, s, d, n):
	a_to_power = pow(a, d, n)
	if a_to_power == 1:
		return True
	for i in xrange(s-1):
		if a_to_power == n - 1:
			return True
		a_to_power = (a_to_power * a_to_power) % n
	return a_to_power == n - 1	
	
def mr(n):
	d = n - 1
	s = 0
	while d % 2 == 0:
		d >>= 1
		s += 1
	for repeat in xrange(25):
		a = 0
		while a == 0:
			a = random.randrange(n)
		if not miller_rabin_pass(a, s, d, n):
			return False
	return True	

def generateKeys():
	si = superIncreasing(2**31, keySize)
	n = sum(si)+1
	while not mr(n):
		n +=1
	w = n / keySize
	while not coprime(n, w):
		w += 1
	pub = [i*w%n for i in si]
	return [[si, w, n], pub]
	
def xor(data, key):
    return ''.join(chr(ord(x) ^ ord(y)) for (x,y) in izip(data, cycle(key)))
		
################################################################################
	
priv, pub = generateKeys()

print "priv\n", priv
print "\npub\n", pub

cipher = enc(xor("f1e64002d25976da3f216d67976c0475364b5f4d", "sg1") + " xored with \"sg1\"", pub)
print "\ncipher\n", cipher

cipher2 = set(cipher) # set = faaaast

plain = xor(dec(cipher, priv)[:40], "sg1")
print "\nplain\n", plain

################################################################################

t = time.clock()
plain = range(len(cipher))
left = len(cipher)

def binToA(b):
	plain = ""
	for i in xrange(0, len(b), 8):
		plain += chr(int(b[i:i+8], 2))
	return plain	

def bruteBin(s, n, b):
	global plain, left
	if n < keySize:
		key = bruteBin(s+pub[n], n+1, b + "1")
		if key == None:
			key = bruteBin(s, n+1, b + "0")
		return key
	else:
		if s in cipher2:
			for i in range(len(cipher)):
				if s == cipher[i]:
					plain[i] = binToA(b)
					left -= 1
					print "\t" + str(s) + "\t:" + plain[i]
					if left == 0:
						plain = ''.join(plain)
						print "\n", xor(plain[:40], "sg1").strip() + " (" +  "%.3f" % (time.clock()-t) + "s)"
						sys.exit(0)
					break

print "\nbruteforcing ...\n",
					
bruteBin(0, 0, "")
