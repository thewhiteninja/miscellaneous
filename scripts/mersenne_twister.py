    
MT = [0 for i in xrange(624)]
index = 0
bitmask_1 = (2 ** 32) - 1
bitmask_2 = 2 ** 31
bitmask_3 = (2 ** 31) - 1

def initialize_generator(seed):
    global MT
    global bitmask_1
    MT[0] = seed
    for i in xrange(1,624):
        MT[i] = ((1812433253 * MT[i-1]) ^ ((MT[i-1] >> 30) + i)) & bitmask_1

def extract_number():
    global index
    global MT
    if index == 0:
        generate_numbers()
    y = MT[index]
    y ^= y >> 11
    y ^= (y << 7) & 2636928640
    y ^= (y << 15) & 4022730752
    y ^= y >> 18
    index = (index + 1) % 624
    return y

def generate_numbers():
    global MT
    for i in xrange(624):
        y = (MT[i] & bitmask_2) + (MT[(i + 1 ) % 624] & bitmask_3)
        MT[i] = MT[(i + 397) % 624] ^ (y >> 1)
        if y % 2 != 0:
            MT[i] ^= 2567483615            
            
good = [24, 58, 25, 37, 53, 43, 0, 60, 33, 46, 51, 33, 52, 36, 34, 53, 4, 0, 20, 36, 4, 44, 23, 60, 5, 31, 40, 26, 56, 24, 27, 59, 33, 15, 51, 36, 12, 26, 33, 12, 61, 14, 8, 36, 3, 16, 25, 15, 36, 7]            
i = 1000000000
ok = False
while i<0x100000000:
    initialize_generator(i)
    ok = False
    for o in xrange(50):
        if extract_number() != good[o]:
            ok = False
            break
    if ok:
        print "Seed", i
        break
    else:
        i += 1
