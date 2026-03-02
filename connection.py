import socket
import hashlib

class Connection:
    def __init__(self, soc: socket.socket, userID: str, isAdmin: bool = False, isMuted = False):
        self.soc = soc
        self.userID = userID
        self.isAdmin = isAdmin
        self.isMuted = isMuted

    def __str__(self):
        return f"{self.soc=}\n{self.userID=}\n{self.isAdmin=}\n{self.isMuted=}"

    def __eq__(self, other):
        if not isinstance(other, Connection): return False
        return self.soc == other.soc and self.userID == other.userID

    def __hash__(self):
        return int.from_bytes(hashlib.sha256(str(self).encode()).digest(), byteorder="little")