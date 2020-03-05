import sys

def run(c):
    res = None
    try:
        f = open(r'\\.\pipe\yolo', 'w+b')
        f.write(c)
        f.flush()
        res = f.read().strip()
        f.close()
        return res
    except IOError as e:
        if e.errno == 2:
            return "Error connecting to pipe"
        else:
            return "Error: Invalid command"

name = run("name")            
while 1:
    try:
        c = raw_input("%s:>"%name)      
    except Exception as e:
        sys.exit(0)  
    if c == "exit":
        sys.exit(0)       
    elif c == "quit":
        print run("quit")
        sys.exit(0)       
    else:
        print run(c)
    