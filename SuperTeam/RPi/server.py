import requests
import json

class Server:
    def __init__(self):
        self.BASE = 'http://sidsrivastava.pythonanywhere.com/'
    
    def sendData(self, h, side1, y, side2):
        print(requests.get(self.BASE + 'update?h='+str(h)+'&side1='+str(side1)+'&y='+str(y)+'&side2='+str(side2)).json()) 
        #print(requests.get(BASE + 'update?h=3&side1=1&y=2&side2=1').json()) # Send to server
        #Format: H victim tile, direction of the victim, yellow victim tile, direction of the victim
    
    def getInfoData(self):
        return requests.get(self.BASE).json()  # To get info data from server