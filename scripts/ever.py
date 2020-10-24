import sys
import os
import platform
import time
import win32api
import win32con
from ctypes import windll

STEP = 4 
  
dc= windll.user32.GetDC(0)
last_check = time.time()
left = True
nb_play = 1

def levelup():
    return windll.gdi32.GetPixel(dc,358,713) == 0x00d156 and windll.gdi32.GetPixel(dc,346,673) == 0x36d96a

def ended():
    return windll.gdi32.GetPixel(dc,239,859) == 0xfffffb and windll.gdi32.GetPixel(dc,514,853) == 0xfffffb

def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)    
       
def info():
    print("Press 'q' to quit")
    while(True):
        if win32api.GetAsyncKeyState(ord('Q')):
            print("exited")
            sys.exit()
        
        p = win32api.GetCursorPos()
        col = windll.gdi32.GetPixel(dc,p[0],p[1])
        print("x:%d y:%d col:%02X%02X%02X"%(p[0], p[1], (col>>16)&0xff, (col>>8)&0xff, (col)&0xff))
        time.sleep(0.001)
       
def play():
    global last_check, left, nb_play
    cx, cy = 360, 768    
    win32api.SetCursorPos((cx, cy))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)      
        
    print("Press 'q' to quit")    
    while(True):
        if win32api.GetAsyncKeyState(ord('Q')):
            print("exited")
            print("%d game played"%(nb_play))
            sys.exit()
            
        if time.time() - last_check > 10:
            last_check = time.time()
            if ended():
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
                click(485, 850)
                time.sleep(2)
                cx, cy = 360, 768    
                win32api.SetCursorPos((cx, cy))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                nb_play += 1
            elif levelup():
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
                click(366, 694)
                time.sleep(2)
                click(485, 850)
                time.sleep(2)
                cx, cy = 360, 768    
                win32api.SetCursorPos((cx, cy))
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                nb_play += 1                
                
        if left:
            cx -= STEP
            if cx < 132:
                left = False
                cx += 2*STEP
        else:
            cx += STEP
            if cx > 593:
                left = True
                cx -= 2*STEP
        
        win32api.SetCursorPos((cx, 840))
        
        time.sleep(0.001)
        
def usage():
    print()
    print("Usage: %s [Options]" % (os.path.basename(sys.argv[0])))
    print()
    print("Options :")
    print("    info")
    print("    play")
    sys.exit(1)
        
print("Starting %s at %s (%s version)" % (os.path.basename(sys.argv[0]), time.asctime(time.localtime(time.time())), platform.architecture()[0]))
if len(sys.argv) < 2:
    usage()
else:
    if sys.argv[1] == "info":
        info()
    elif sys.argv[1] == "play":
        play()
    else:
        usage()
        
        
    


