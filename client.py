import sys
from pprint import pprint
import Pyro4
import Pyro4.util

class Client:
    def __init__(self, username, keyphrase):
        self.username = username
        self.keyphrase = keyphrase
        self.token = None
        self.orders = []

    def set_server(self, server):
        self.server = server

    def login(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        self.token = self.server.login(self.username, self.keyphrase)
        if not self.token:
            print("ERROR: Failed to obtain token!")
            return
        print("INFO: Logged in successfully!")

    def logout(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.logout(self.token):
            print("ERROR: Failed to logout!")
            return
        print("INFO: Logged out successfully!")

    def create_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.server.create_account(self.username, self.keyphrase):
            print("ERROR: Failed to create account!")
            return
        print("INFO: New account created!")
    
    def delete_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.delete_account(self.token):
            print("ERROR: Failed to delete account")
            return
        print("INFO: Successfully deleted account!")
        self.token = None

    def make_order(self, item_name, quantity, address):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        order_id = self.server.make_order(self.token, item_name, quantity, address)
        self.orders.append(order_id)
        print(f"INFO: Created new order with id {order_id}")

    def cancel_order(self, order_id):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.cancel_order(self.token, order_id):
            print("ERROR: Failed to cancel order!")
            return
        self.orders.remove(order_id)
        print(f"INFO: Successfully cancelled order with id {order_id}")
        

    def view_orders(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        orders = self.server(self.token)
        pprint(orders)

    def show_items(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        pprint(self.server.show_items())
    
sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    jh = Pyro4.Proxy("PYRONAME:example.just_hungry")
    client = Client("vvvm23", "foobar")
    client.set_server(jh)
    client.create_account()
    client.login()


    client.logout()
