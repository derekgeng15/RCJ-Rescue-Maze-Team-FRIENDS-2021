import requests
import json

class Server:
    def __init__(self):
        self.BASE = 'http://sidsrivastava.pythonanywhere.com/'
    
    def sendData(self, path):
        print(requests.get(self.BASE + 'update?string='+path).json())
        #print(requests.get(BASE + 'update?h=3&side1=1&y=2&side2=1').json()) # Send to server
        #Format: H victim tile, direction of the victim, yellow victim tile, direction of the victim
    
    def getInfoData(self):
        return requests.get(self.BASE).json()  # To get info data from server