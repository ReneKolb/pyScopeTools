from multiprocessing.managers import BaseManager
from ctypes import c_int, c_char_p, cdll
from os import closerange, write

# setup library
libc = cdll.LoadLibrary("LQUGPlus_c.dll")

# tell ctypes how to call function
libc.Gwrite.restype = c_int
libc.Gread.restype  = c_char_p

# wrapper for access to the functions
class LibC:
    Gwrite = staticmethod(libc.Gwrite)
    Gread  = staticmethod(libc.Gread)

# setup manager
manager = BaseManager(address=("localhost", 0))
manager.register("LibC", LibC)

server = manager.get_server()
# tell caller the port and auth key to access the manager with
write(1, str(server.address[1]).encode("ascii"))
write(1, b"\n")
write(1, server.authkey) # write raw authkey bytes
closerange(0, 3) # close stdin, stdout, stderr

server.serve_forever()