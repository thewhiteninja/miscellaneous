#!/usr/bin/python           

import socket               

s = socket.socket()         
host = "0.0.0.0"            
port = 445                  
s.bind((host, port))        

f = open("/var/www/smb.txt", "w")

s.listen(5)                 
while True:
   c, addr = s.accept()     
   f.write(str(addr[0]) + "\n")
   f.flush()
   c.close()              

f.close()
