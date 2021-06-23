from server import Server

s = Server()

s.sendData(4, 3, 8, 1)

print(s.getInfoData())