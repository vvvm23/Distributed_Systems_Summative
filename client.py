import sys
from pprint import pprint
import Pyro4
import Pyro4.util
import time

# Client program class
class Client:
    def __init__(self, server):
        self.username = None
        self.keyphrase = None
        self.token = None
        self.set_server(server)

    def set_username(self, username):
        self.username = username

    def set_keyphrase(self, keyphrase):
        self.keyphrase = keyphrase

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
            return False

        if not self.username or not self.keyphrase:
            print("ERROR: No username and password specified!")
            return False

        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        # Get session token
        self.token = self.server.forward_request("login", username=self.username, keyphrase=self.keyphrase)
        if not self.token:
            print("ERROR: Failed to obtain token!")
            return False
        print("INFO: Logged in successfully!")
        return True

    # Client logout function
    def logout(self):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.token:
            print("ERROR: No token provided")
            return False
        if not self.server.forward_request("logout", user_token=self.token):
            print("ERROR: Failed to logout!")
            return False
        print("INFO: Logged out successfully!")
        self.token = None
        self.username = None
        self.keyphrase = None
        return True

    # Create new account
    def create_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.username or not self.keyphrase:
            print("ERROR: No username and password specified!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.server.forward_request("create_account", username=self.username, keyphrase=self.keyphrase):
            print("ERROR: Failed to create account!")
            return False
        print("INFO: New account created!")
        return True
    
    # Delete account
    def delete_account(self):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.token:
            print("ERROR: No token provided")
            return False
        if not self.server.forward_request("delete_account", user_token=self.token):
            print("ERROR: Failed to delete account")
            return False
        print("INFO: Successfully deleted account!")
        self.username = None
        self.keyphrase = None
        self.token = None
        return True

    # Make a new order
    def make_order(self, item_name, quantity, address):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.token:
            print("ERROR: No token provided")
            return False
        # Get the order id
        result = self.server.forward_request("make_order", user_token=self.token, item_name=item_name, quantity=quantity, address=address)

        if result == None:
            print("ERROR: Post Code was invalid")
            return False

        order_id = result[0]
        lonlat = (result[1]['longitude'], result[1]['latitude'])

        if order_id:
            print(f"INFO: Created new order with id {order_id}")
            print(f"INFO: Your order will be delivered to Longitude: {lonlat[0]}, Latitude: {lonlat[1]}")
        else:
            print("ERROR: Failed to make new order!")
            return False
        return True

    # Cancel a order
    def cancel_order(self, order_id):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.token:
            print("ERROR: No token provided")
            return False
        if not self.server.forward_request("cancel_order", user_token=self.token, order_id=order_id):
            print("ERROR: Failed to cancel order!")
            return False
        print(f"INFO: Successfully cancelled order with id {order_id}")
        return True
        
    # View active orders
    def view_orders(self):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend servr!")
            return False
        if not self.token:
            print("ERROR: No token provided")
            return False
        # Returns list of orders
        orders = self.server.forward_request("view_orders", user_token=self.token)
        print("OrderID\t\t\tItem\tQuantity\tPost Code\tLongitude\t\tLatitude\t\tTotal Cost\tStatus\t\tETA")
        for order in orders:
            print(f"{order[0]}\t{order[1]}\t{order[2]}\t\t{order[3]}\t\t{order[4]}\t\t{order[5]}\t\t{order[6]}\t\t{order[7]}\t{order[8]}")
        return True

    # Show all available items
    def show_items(self):
        if not self.server:
            print("ERROR: No server defined!")
            return False
        if not self.ping_server():
            print("ERROR: Unable to connect to frontend server!")
            return False
        # Returns list of items
        items = self.server.forward_request("show_items")
        pprint(items)
        return True
    
# Set the remote exception hook
sys.excepthook = Pyro4.util.excepthook
if __name__ == "__main__":
    ns = Pyro4.locateNS() # Locate the name server
    if not ns:
        print("ERROR: Cannot find Name Server!")
        exit()

    servers = [(name, uri) for name, uri in ns.list(prefix="just_hungry.front_end").items()]
    if not len(servers):
        print("ERROR: Cannot find frontend server!")
        exit()
    
    front_server = Pyro4.Proxy(servers[0][1])
    try:
        front_server._pyroBind()
    except Exception as e:
        print("ERROR: Cannot connect to frontend server.")
        exit()

    client = None
    try:
        while True:
            print()
            if client:
                print(f"Currently logged in as {client.username}")
            else:
                print(f"Currently logged in anonymously")

            print("Select Option:")
            if client:
                print("\t1. Make Order")
                print("\t2. Cancel Order")
                print("\t3. View Orders")
                print("\t4. Show Items")
                print("\t5. Logout")
                print("\t6. Delete Account")
                print("\t0. Exit")
            else:
                print("\t1. Create Account")
                print("\t2. Login")
                print("\t0. Exit")

            menu_action = int(input("> "))

            # Create Account
            if not client and menu_action == 1:
                print("Enter username of new account.")
                input_username = input("> ")
                if not input_username or input_username == "":
                    print("ERROR: Invalid Username!")
                    continue
                print("Enter keyphrase of new account.")
                input_keyphrase = input("> ")
                if not input_keyphrase or input_keyphrase == "":
                    print("ERROR: Invalid Keyphrase!")
                    continue
                client = Client(front_server)
                client.set_username(input_username)
                client.set_keyphrase(input_keyphrase)
                if not client.create_account():
                    client = None
                    continue
                if not client.login():
                    client = None
                    continue
            # Login
            elif not client and menu_action == 2:
                print("Enter username of existing account.")
                input_username = input("> ")
                if not input_username or input_username == "":
                    print("ERROR: Invalid Username!")
                    continue
                print("Enter keyphrase of existing account.")
                input_keyphrase = input("> ")
                if not input_keyphrase or input_keyphrase == "":
                    print("ERROR: Invalid Keyphrase!")
                    continue
                client = Client(front_server)
                client.set_username(input_username)
                client.set_keyphrase(input_keyphrase)
                if not client.login():
                    client = None
                    continue
            # Show Items
            elif (client and menu_action == 4):
                client.show_items()
            # Make Order
            elif client and menu_action == 1:
                print("Enter name of item you wish to order.")
                input_name = input("> ")
                print("Enter quantity.")
                input_quantity = input("> ")
                if not input_quantity.isnumeric():
                    print("ERROR: Invalid quantity")
                    continue
                input_quantity = int(input_quantity)
                if input_quantity <= 0:
                    prin("ERROR: Invalid quantity")
                    continue
                print("Enter post code.")
                input_post = input("> ")
                client.make_order(input_name, input_quantity, input_post)
            # Cancel Order
            elif client and menu_action == 2:
                print("Enter order id.")
                input_order = input("> ")
                client.cancel_order(input_order)
            # View Orders
            elif client and menu_action == 3:
                client.view_orders()
            # Logout
            elif client and menu_action == 5:
                if not client.logout():
                    continue
                client = None
            # Delete Account
            elif client and menu_action == 6:
                if not client.delete_account():
                    continue
                client = None
            elif menu_action == 0:
                print("Goodbye..")
                logout_attempts = 0
                while not client.logout() and logout_attempts < 5:
                    print("ERROR: Failed to logout on exit. Retrying..")
                    logout_attempts+=1
                    time.sleep(1)
                break
            else:
                print("ERROR: Unknown Option")
                continue
    # Ensure if we crash for whatever reason to logout the client
    except Exception as e:
        if client:
            logout_attempts = 0
            while not client.logout() and logout_attempts < 5:
                print("ERROR: Failed to logout on Exception. Retrying..")
                logout_attempts+=1
                time.sleep(1)
        raise e
