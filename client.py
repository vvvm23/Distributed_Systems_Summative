import sys
from pprint import pprint
import Pyro4
import Pyro4.util

# Client program class
class Client:
    def __init__(self, username, keyphrase):
        self.username = username
        self.keyphrase = keyphrase
        self.token = None
        self.orders = []

    # Set the front end server the client interacts with
    def set_server(self, server):
        self.server = server

    # Ping the primary server and see if it is up
    def ping_server(self):
        try:
            self.server._pyroBind()
        except Exception as e:
            return False
        return True

    # Client login function
    def login(self):
        if not self.server:
            print("ERROR: No server defined!")
            return

        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        # Get session token
        self.token = self.server.forward_request("login", username=self.username, keyphrase=self.keyphrase)
        if not self.token:
            print("ERROR: Failed to obtain token!")
            return
        print("INFO: Logged in successfully!")

    # Client logout function
    def logout(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.forward_request("logout", user_token=self.token):
            print("ERROR: Failed to logout!")
            return
        print("INFO: Logged out successfully!")

    # Create new account
    def create_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.server.forward_request("create_account", username=self.username, keyphrase=self.keyphrase):
            print("ERROR: Failed to create account!")
            return
        print("INFO: New account created!")
    
    # Delete account
    def delete_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.forward_request("delete_account", user_token=self.token):
            print("ERROR: Failed to delete account")
            return
        print("INFO: Successfully deleted account!")
        self.token = None

    # Make a new order
    def make_order(self, item_name, quantity, address):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        # Get the order id
        order_id = self.server.forward_request("make_order", user_token=self.token, item_name=item_name, quantity=quantity, address=address)
        if order_id:
            self.orders.append(order_id)
            print(f"INFO: Created new order with id {order_id}")
        else:
            print("ERROR: Failed to make new order!")

    # Cancel a order
    def cancel_order(self, order_id):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        if not self.server.forward_request("cancel_order", user_token=self.token, order_id=order_id):
            print("ERROR: Failed to cancel order!")
            return
        self.orders.remove(order_id)
        print(f"INFO: Successfully cancelled order with id {order_id}")
        
    # View active orders
    def view_orders(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        if not self.token:
            print("ERROR: No token provided")
            return
        # Returns list of orders
        orders = self.server.forward_request("view_orders", user_token=self.token)
        pprint(orders)

    # Show all available items
    def show_items(self):
        if not self.server:
            print("ERROR: No server defined!")
            return
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return
        # Returns list of items
        items = self.server.forward_request("show_items")
        pprint(items)
    
# Set the remote exception hook
sys.excepthook = Pyro4.util.excepthook
if __name__ == "__main__":
    ns = Pyro4.locateNS() # Locate the name server
    servers = [(name, uri) for name, uri in ns.list(prefix="just_hungry.front_end").items()]
    if not len(servers):
        print("ERROR: Cannot find frontend server!")
        exit()
    
    front_server = Pyro4.Proxy(servers[0][1])

    client = Client("vvvm23", "foobar")
    client.set_server(front_server)
    client.create_account()
    client.login()
    client.make_order("Carrot", 400, "CA130DQ")
    client.logout()
    client.login()
    client.show_items()
    client.make_order("Cake", 2, "DH11QL")
    client.make_order("Cheese", 69, "foobarstreet")
    client.view_orders()
    client.cancel_order(client.orders[1])
    client.view_orders()

    client.delete_account()
