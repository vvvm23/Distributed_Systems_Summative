import sys
import Pyro4
import Pyro4.util
import urllib.request
from collections import defaultdict
import json
import random
'''
    Commands:
        User Login
        Create Account
        Make new order
        View orders
        Cancel a order
        Edit existing order
'''

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class JustHungry:
    def __init__(self):
        self.is_working = True
        self.is_master = False
        
        self.ns = Pyro4.locateNS()
        if not self.ns:
            print("ERROR: Failed to locate Name Server. Exiting..")

        # user_name: (keyphrase, logged_in?, orders)
        # order = [order_id, item_name, quantity, address, price, status, eta]
        self.users = defaultdict(lambda: [None, None, []])
        # token: username
        self.user_tokens = defaultdict(lambda: None)
        self._init_items()
    def ping_respond(self):
        # TODO: pyroSync may be useful here <04-03-20, alex> #
        return self.is_working
    def _init_items(self):
        # item_name: price in pence
        self.items = defaultdict(lambda: None)
        self.items = {
                "Potato": 23, "Onion": 30, "Carrot": 20,
                "Apple": 42, "Orange": 50, "Banana": 46,
                "Beef": 420, "Pork": 299, "Chicken": 399,
                "Cheese": 119, "Milk": 119, "Bread": 79,
                "Cake": 399, "Icecream": 129, "Biscuit": 99
        }

    def set_master(self, state):
        self.is_master = state

    def promote_master(self):
        slaves = [(name, uri) for name, uri in self.ns.list(prefix="just_hungry.back_end").items()]
        for s in slaves:
            try:
                sl = Pyro4.Proxy(s[1])
                sl._pyroBind()
            except Exception as e:
                continue
            if not sl.ping_respond():
                continue
            
            sl.set_master(False)

        print("INFO: This server is now the new Master Server")
        self.is_master = True

    def master_sync(self):
        if self.is_master:
            slaves = [(name, uri) for name, uri in self.ns.list(prefix="just_hungry.back_end").items()]
            for s in slaves:
                try:
                    sl = Pyro4.Proxy(s[1])
                    sl._pyroBind()
                except Exception as e:
                    continue
                if not sl.ping_respond():
                    continue
                sl.slave_sync(self.users, self.user_tokens)


    def slave_sync(self, users, user_tokens):
        if not self.is_master:
            self.users = defaultdict(lambda: [None, None, []])
            for u in users:
                self.users[u] = users[u].copy()

            self.user_tokens = defaultdict(lambda: None)
            for t in user_tokens:
                self.user_tokens[t] = user_tokens[t]

            #self.users = users.copy()
            #self.user_tokens = user_tokens.copy()
            print("Synced successfully.")


    def disable_server(self):
        self.is_working = False

    def enable_server(self):
        self.is_working = True

    # Check if postcode is valid using external service
    def validate_postcode(self, code):
        print(f"DEBUG: Checking https://api.postcodes.io/postcodes/{code}/validate")
        result = False
        with urllib.request.urlopen(f"https://api.postcodes.io/postcodes/{code}/validate") as res:
            json_res = json.loads(res.read().decode('utf-8'))
            print(json_res)
            result = json_res['result']

        return result

    # Login user and obtain session token
    def login(self, username, keyphrase):
        if self.users[username][1]:
            print(f"Failed to authenticate {username}")
            return None 

        if self.users[username][0] == None:
            print(f"Failed to authenticate {username}")
            return None

        if self.users[username][0] == keyphrase:
            token = '%020x' % random.randrange(16 ** 20) 
            self.user_tokens[token] = username
            self.users[username][1] = True
            print(f"Starting new session as {username} with token {token}")
            return token
        else:
            print(f"Failed to authenticate {username}")
            return None 

    # Logout user if token is valid
    def logout(self, user_token):
        logout_user = self.user_tokens[user_token]
        if logout_user:
            self.user_tokens.pop(user_token)
            self.users[logout_user][1] = False
            print(f"Logged out {logout_user}")
            return True
        else:
            print(f"Failed to logout.")
            return False

    # Create a new account
    def create_account(self, username, keyphrase):
        if self.users[username][0] == None:
            self.users[username][0] = keyphrase
            self.users[username][1] = False
            print(f"Created account {username}!")
            return True
        else:
            print(f"Failed to create account.")
            return False

    # Delete an existing account
    def delete_account(self, user_token):
        delete_user = self.user_tokens[user_token]
        if delete_user:
            self.logout(user_token)
            self.users.pop(delete_user)
            return True
        else:
            print(f"Failed to delete user.")
            return False

    # Make a new order
    def make_order(self, user_token, item_name, quantity, address):
        user = self.user_tokens[user_token]
        if user == None:
            return None
        if self.items[item_name] == None:
            return None
        if quantity < 1:
            return None
        if address == "" or not address:
            return None 
        if not self.validate_postcode(address):
            print("ERROR: Invalid postcode!")
            return None

        order_id = '%020x' % random.randrange(16 ** 20) 
        self.users[user][2].append(
                [order_id, item_name, quantity, address, self.items[item_name]*quantity, "processing", "3 days"]
            )
        print("Successfully placed order")
        return order_id 

    # View orders by a user
    def view_orders(self, user_token):
        user = self.user_tokens[user_token]
        if user == None:
            return None
        return self.users[user][2]

    # Show available items
    def show_items(self):
        return self.items

    # Cancel an existing order
    def cancel_order(self, user_token, order_id):
        user = self.user_tokens[user_token]
        if user == None:
            return False
        
        for i, order in enumerate(self.users[user][2]):
            if order[0] == order_id:
                self.users[user][2].pop(i)
                return True

        return False
sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    server_rand_id = '%020x' % random.randrange(16 ** 20) 
    Pyro4.Daemon.serveSimple(
                {
                    JustHungry: f"just_hungry.back_end.{server_rand_id}"  
                },
                ns=True)

