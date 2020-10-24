from threading import Timer
import urllib2
import time
import sys

class RepeatingTimer():
    def __init__(self, interval, function):
        self.function = function
        self.interval = interval
        self.current_timer = None
 
    def start(self):
        self.callback()

    def stop(self):
        try:
            self.current_timer.stop()
        except:
            pass
    
    def callback(self):
        self.function()
        self.current_timer = Timer(self.interval, self.callback)
        self.current_timer.start()
        
def check():
    global t
    sys.stdout.write('\b'*50)
    sys.stdout.write("Check at " + time.strftime("%H:%M:%S"))
    response = urllib2.urlopen('https://ws.ovh.com/order/dedicated/servers/ws.dispatcher/getPossibleOptionsAndAvailability?callback%3Dangular.callbacks._2%26params%3D%7B%22sessionId%22%3A%22classic%2Fanonymous-a65611f1708af324a8410d0174a66c53%22%2C%22billingCountry%22%3A%22KSFR%22%2C%22dedicatedServer%22%3A%22142sk1%22%2C%22installFeeMode%22%3A%22directly%22%2C%22duration%22%3A%221m%22%7D')
    html = response.read()
    if html.find("\"availability\":-1") == -1:
        go()
        t.stop()
        
def go():
    print "GO \a"
    Timer(1, go).start()        
        
t = RepeatingTimer(30,check)
t.start()