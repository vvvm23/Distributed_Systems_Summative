import sys
import Pyro4
import Pyro4.util

# Expose this class as a Pyro4 object
@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FrontServer:
    def __init__(self):
        self.primary = None # Primary Server Reference
        self.ns = Pyro4.locateNS() # Locate the Name Server
        if not self.ns:
            print("ERROR: Failed to locate Name Server. Exiting..")
            exit()
        self.methods = None
        if not self.set_primary(): # Search for the primary server
            print("ERROR: Failed to find primary server. Exiting..")
            exit()

    # Search for primary server and set it
    def set_primary(self):
        servers = [(name, uri) for name, uri in self.ns.list(prefix="just_hungry.back_end").items()]
        for s in servers:
            active = Pyro4.Proxy(s[1])

            # Check if the server is up
            try:
                active._pyroBind()
            except Exception as e:
                continue
            if active.ping_respond():
                # If it is, set as the new primary
                self.primary = active
                self.primary.promote_master() # Promote the server to master
                # Get all methods from the primary server
                self.methods = {
                    "login": active.login,
                    "logout": active.logout,
                    "create_account": active.create_account,
                    "delete_account": active.delete_account,
                    "make_order": active.make_order,
                    "cancel_order": active.cancel_order,
                    "view_orders": active.view_orders,
                    "show_items": active.show_items
                }
                return True
        return False

    # Check if the primary server is up
    def ping_primary(self):
        try:
            self.primary._pyroBind()
            if self.primary.ping_respond():
                return True
        except Exception as e:
            return False
        return False

    # Forward requests from client to backend server
    def forward_request(self, method, **args):
        VALID_METHODS = set(["login", "logout", "create_account", "delete_account", "make_order", "cancel_order", "view_orders", "show_items"])

        if not method in VALID_METHODS:
            print("ERROR: Unknown method!")
            return False

        # Check if primary is up
        if not self.ping_primary():
            print("ERROR: Current primary is down! Finding new server..")
            # If not, find a new primary
            if not self.set_primary():
                print("ERROR: Failed to find new primary server!")
                return False

        # Get the corresponding method and call it remotely.
        server_result = self.methods[method](**args)

        # Tell the primary server to sync with slaves
        self.primary.master_sync()
        return server_result

# Set remote exception hook
sys.excepthook = Pyro4.util.excepthook
if __name__ == "__main__":
    Pyro4.Daemon.serveSimple({
            FrontServer: "just_hungry.front_end"
        }, ns=True)

