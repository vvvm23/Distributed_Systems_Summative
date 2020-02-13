import sys

import Pyro4
import Pyro4.util

class Client:
    def __init__(self):
        pass
    
    def connect(self, server):
        self.server = server

    def add(self, x, y):
        print(f"{x} + {y} = {self.server.add(x,y)}")

    def subtract(self, x, y):
        print(f"{x} - {y} = {self.server.subtract(x,y)}")

    def crash(self):
        X = [1,2,3]
        print(X[3])

sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    jh = Pyro4.Proxy("PYRONAME:example.just_hungry")
    client = Client()

    if not jh.create_account("mrsushidog", "d68f44c5379310a71203"):
        print("failed to make account")
    token = jh.login("mrsushidog", "d68f44c5379310a71203")
    print(f"My token is {token}")
    jh.logout(token)
