from __future__ import print_function
from subprocess import Popen, PIPE 
from multiprocessing.managers import BaseManager
import atexit
import time

PYTHON_32BIT_PATH = r"C:\Users\APQ\Anaconda2_32bit\pythonw.exe"

class LQ_GPIBComm:
    def __init__(self, address=1, eol='\r\n'):

        self.address = address
        self.eol = eol

        p = Popen([PYTHON_32BIT_PATH, "delegate.py"], stdout=PIPE)

        atexit.register(p.terminate)

        port = int(p.stdout.readline())
        authkey = p.stdout.read()

        m = BaseManager(address=("localhost", port), authkey=authkey)
        m.connect()

        # tell manager to expect an attribute called LibC
        m.register("LibC")

        # access and use libc
        self.UGPlusLib = m.LibC()


        self.do_init_oszi()    
    
    def do_init_oszi(self):
        self.writeline("*CLS") #clear status

    def readline(self):
        res = ""
        break_counter = 0
        while not self.eol in res:
            append = self.UGPlusLib.Gread(self.address)
            if len(append)==0:
                time.sleep(0.1)
                break_counter += 1
                if break_counter > 20: #2sec timeout
                    raise Exception("Line termination character is not received within the timeout")
            else:
                res += append
                break_counter = 0

        return res
        
    def read(self, bytes=1):
        return self.readline_raw()
        #return self.connection.read(bytes)
        
    def readline_raw(self, min_bytes):
        return self.readline()#self.inst.read_raw()

    def write(self, message):
        #self.writeline(message)
        self.UGPlusLib.Gwrite(self.address, message)
    
    def writeline(self, message):
        #self.inst.write(message) #will append eol chars
        self.write(message+self.eol)
        
    def query(self, msg, timeout=None):
        self.writeline(msg)
        return self.readline()