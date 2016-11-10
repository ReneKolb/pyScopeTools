from __future__ import print_function
import serial
import io

class SerialComm:

    def __init__(self, address, baudrate=9600, timeout=2000, eol='\r\n'):
        self.serial = serial.Serial(port=address, baudrate=baudrate)
        self.serial.timeout = timeout
        self.eol = eol
        self.b_eol = eol.encode('ascii')
        
    def readline(self):
        out = ""
        while not self.eol in out:
            out += self.serial.read(self.serial.inWaiting()).decode('ascii')
        return out.replace(self.eol,'\n')

        
    def read(self, bytes=1):
        return self.serial.read(bytes).decode('ascii')
        
    def readline_raw(self):
        out = b""
        while not self.b_eol in out:
            out += self.serial.read(self.serial.inWaiting())
        return out.replace(self.b_eol,b'\n')

    def write(self, message):
        self.writeline(message)
    
    def writeline(self, message):
        self.serial.write((message+self.eol).encode('ascii'))
        
    def query(self, msg, timeout=None):
        oldTimeout = self.serial.timeout
        if timeout:
            self.serial.timeout = timeout
        self.write(msg)
        result = self.readline()
        self.serial.timeout = oldTimeout
        return result