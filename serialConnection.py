from __future__ import print_function
import serial
import io

class SerialComm:

    def __init__(self, address, baudrate='9600', eol='\r\n'): #eol = None means universal EOL is used! all eol received (\n \r or \r\n) are translated to \n
        self.serial = serial.Serial(port=address, baudrate=baudrate)
        self.serial.timeout = 2000 # adjust to 2sec, but when downloading Data increase to 10 sec! and afterwrds back to 2sec
        
    def readline(self):
        out = ""
        while not '\r\n' in out:
            out += self.serial.read(self.serial.inWaiting()).decode('ascii')
        return out    

        
    def read(self, bytes=1):
        return self.serial.read(bytes).decode('ascii')
        #return self.connection.read(bytes)
        
    def read_raw(self, bytes=1):
        return self.serial.read(bytes)

    def write(self, message):
        self.writeline(message)
    
    def writeline(self, message):
        self.serial.write((message+"\r\n").encode('ascii'))
        
    def query(self, msg, timeout=None):#, append_eol=True):
        oldTimeout = self.serial.timeout
        if timeout:
            self.serial.timeout = timeout
        self.write(msg)#, append_eol)
        result = self.readline()
        self.serial.timeout = oldTimeout
        return result