import sys
from pprint import pprint
import Pyro4
import Pyro4.util

class Client:
    def __init__(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def create_account(self):
        pass
    
    def delete_account(self):
        pass

    def make_order(self):
        pass

    def cancel_order(self):
        pass

    def view_orders(self):
        pass

    def show_items(self):
        pass
    
sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    jh = Pyro4.Proxy("PYRONAME:example.just_hungry")
    client = Client()

    if not jh.create_account("mrsushidog", "d68f44c5379310a71203"):
        print("failed to make account")
    token = jh.login("mrsushidog", "d68f44c5379310a71203")
    print(f"My token is {token}")
    pprint(jh.show_items())
    order1 = jh.make_order(token, "Banana", 69, "Foobar street, Mogadishu")
    order2 = jh.make_order(token, "Beef", 4, "Foobar street, Mogadishu")
    pprint(jh.view_order(token))
    jh.cancel_order(token, order1)
    pprint(jh.view_order(token))
    jh.logout(token)
