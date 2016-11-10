from __future__ import print_function
import time
import numpy as np
import traceback


class Scope:
    """Object modeling the oszilloscope

    Working example:
#####
import numpy as np
import matplotlib.pyplot as plt
import scope

#myscope=scope.Scope(u'GPIB0::1::INSTR', debug=True)
myscope=scope.Scope("COM1", debug=False)

x,data=myscope.readScope(fast_mode=False)

plt.plot(x,data)
plt.show()
#####
    """

#using serial (COM) (@baudrate: 9600)
#   normal mode: 5.3sec
#   fast mode:   2.7sec
#using GPIB
#   normal mode: 0.55sec
#   fast mode:   0.37sec

    def __init__(self, address, baudrate=9600, timeout=6000, debug = False):
        """Create the scope object with given parameters

        Arguments:
        address - the com port to be used, eg "COM1"
                  or a GPIB address like "u'GPIB0::1::INSTR'"
                  the address is obtained by using GPIBConnection.list_devices()

        Keyword arguments:
        baudrate - serial baudrate that is used (default: 9600)
        timeout - set the timeout. NOTICE: a serial connection needs a long timeout, so the default value is 6sec!
        debug - switch the command line output
        """
        if "COM" in address:
            import serialConnection
            self.con = serialConnection.SerialComm(address, baudrate, timeout=timeout, eol='\r\n')
        elif "GPIB" in address:
            import GPIBConnection
            self.con = GPIBConnection.GPIBComm(address, timeout=timeout, eol='\r\n')
        else:
            print("No valid address type")
        self.debug = debug
        
    def readScope(self, channel="CH1", fast_mode=True):
        """Read the data from scope without changing settings

        Keyword arguments:
        channel - channel to be read (default: "CH1"), also possible "CH1CH2"
        fast_mode - use 1byte vs use 2bytes per data point
        """
        byte_wid = 1 if fast_mode else 2
        read_ch1 = "CH1" in channel
        read_ch2 = "CH2" in channel
        if not read_ch1 and not read_ch2:
            print("No channels selected.")
            return
        # catch possible exceptions
        try:
            t0 = time.time()
            self.con.writeline("HEAD ON")
            #freeze the Oszi
            if self.debug: print("freeze oszi")
            self.con.writeline("ACQ:STATE 0")
            #setup encoding
            if self.debug: print("setup encoding")
            self.con.writeline("DAT:ENC RIB")
            self.con.writeline("DAT:WID "+str(byte_wid))
            #setup start and endpoint
            if self.debug: print("setup start & end value")
            self.con.writeline("DAT:STAR 1")
            self.con.writeline("DAT:STOP 2500")
            #now read CH1
            if read_ch1:
                if self.debug: print("request CH1")
                self.con.writeline("DAT:SOU CH1")
                out = self.con.query("WFMPRe:XINCR?;XZERO?;YMULT?;YZERO?;YOFF?") #only request neccessary parameters (not complete WFMPRe?)
                #maybe also request XUNIT and YUNIT? but it seems to be always sec and Volts
#                out = self.con.readline()
#                if out[-1] == 'E':
#                    out += "1"
                params = {}
                out = out.split(';')
                for s in out:
                     d = s.split(" ") #now split on the space sign
                     params[d[0][8:]] = d[1]

                self.con.writeline("CURV?") #request the curve data    
                out = self.con.readline_raw()
                out = out[13:-1] #drop the first 13 chars: ":CURVE #45000" and the last '\n'
                #so now out contains only the bytes of the curve data
                
                if byte_wid == 1:
                    if len(out) > 2500: #should not happen
                        out = out[:2500]
                        print("1: must drop one")
                    data1 = np.fromstring(out, dtype='b')
                else:
                    if len(out) > 5000: #should not happen
                        out = out[:5000]
                        print("2: must drop one")
                    data1 = np.fromstring(out, dtype='>i2')
                    
                # add y-offset to data
                data1 = np.add(data1,np.ones(data1.shape)*(-float(params['YOFF'])))
                # multiply value to get the actual voltage
                data1 *= float(params['YMULT'])
            #now read CH2    
            if read_ch2:            
                if self.debug: print("request CH2")
                self.con.writeline("DAT:SOU CH2")
                self.con.writeline("WFMPRe:XINCR?;XZERO?;YMULT?;YZERO?;YOFF?") #only request neccessary parameters (not complete WFMPRe?)
                #maybe also request XUNIT and YUNIT? but it seems to be always sec and Volts
                out = self.con.readline()
                
                params = {}
                out = out.split(';')
                for s in out:
                     d = s.split(" ") #now split on the space sign
                     params[d[0][8:]] = d[1]

                self.con.writeline("CURV?") #request the curve data
                out = self.con.readline_raw()
                out = out[13:-1]                
                
                if byte_wid == 1:
                    if len(out) > 2500:
                        out = out[:2500]
                        print("1: must drop one")
                    data2 = np.fromstring(out, dtype='b')
                else:
                    if len(out) > 5000:
                        out = out[:5000] #drop another char  (only neccessary when using serial connection COM port)??
                        print("2: must drop one")
                    data2 = np.fromstring(out, dtype='>i2')
                    
                # add offset to data
                data2 = np.add(data2,np.ones(data2.shape)*(-float(params['YOFF'])))
                # multiply to get voltage
                data2 *= float(params['YMULT'])
    
            # create x axis
            x = np.arange(float(params['XZERO']),
                            float(params['XZERO'])+2500*float(params['XINCR']),
                            float(params['XINCR']))    
                            
            
            
            #finally unfreeze the Oszi
            if self.debug: print("unfreeze oszi")
            self.con.writeline("ACQ:STATE 1")
            if self.debug: print("done")
            if self.debug:
                print("Reading took: "+str(time.time() - t0)+"sec")    
            if read_ch1 and read_ch2:
                return x, data1, data2
            if read_ch1:
                return x, data1
            if read_ch2:
                return x, data2
            else:
                return (0,0)
             
        except:
            # error in read
            traceback.print_exc()
            try:
                print("An Error occurred")
                self.con.close()
                return (0,0)
            except:
                print("Error Closing")
                return (0,0)

