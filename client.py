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
        # self.token = self.server.login(self.username, self.keyphrase)
        self.token = self.server.forward_request("login", username=self.username, keyphrase=self.keyphrase)
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
        # if not self.server.logout(self.token):
        if not self.server.forward_request("logout", user_token=self.token):
            print("ERROR: Failed to logout!")
            return
        print("INFO: Logged out successfully!")

    def create_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        # if not self.server.create_account(self.username, self.keyphrase):
        if not self.server.forward_request("create_account", username=self.username, keyphrase=self.keyphrase):
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
        # if not self.server.delete_account(self.token):
        if not self.server.forward_request("delete_account", user_token=self.token):
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
        # order_id = self.server.make_order(self.token, item_name, quantity, address)
        order_id = self.server.forward_request("make_order", user_token=self.token, item_name=item_name, quantity=quantity, address=address)
        self.orders.append(order_id)
        print(f"INFO: Created new order with id {order_id}")

    def cancel_order(self, order_id):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        # if not self.server.cancel_order(self.token, order_id):
        if not self.server.forward_request("cancel_order", user_token=self.token, order_id=order_id):
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
        # orders = self.server.view_orders(self.token)
        orders = self.server.forward_request("view_orders", user_token=self.token)
        pprint(orders)

    def show_items(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        # pprint(self.server.show_items())
        pprint(self.server.forward_request("show_items"))
    
sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    # jh = Pyro4.Proxy("PYRONAME:example.just_hungry")
    ns = Pyro4.locateNS()
    servers = [(name, uri) for name, uri in ns.list(prefix="just_hungry.front_end").items()]
    if not len(servers):
        print("ERROR: Cannot find frontend server!")
        exit()
    
    front_server = Pyro4.Proxy(servers[0][1])

    client = Client("vvvm23", "foobar")
    client.set_server(front_server)
    client.create_account()
    client.login()
    client.make_order("Carrot", 400, "foobar avenue")
    client.logout()
    client.login()
    client.show_items()
    client.make_order("Cake", 2, "foobar street")
    client.make_order("Cheese", 69, "foobar street")
    client.view_orders()
    client.cancel_order(client.orders[1])
    client.view_orders()

    client.delete_account()
