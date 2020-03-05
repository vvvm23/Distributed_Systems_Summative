import sys
import Pyro4
import Pyro4.util

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FrontServer:
    def __init__(self):
        self.primary = None
        self.ns = Pyro4.locateNS()
        if not self.ns:
            print("ERROR: Failed to locate Name Server. Exiting..")
            exit()
        self.methods = None
        if not self.set_primary():
            print("ERROR: Failed to find primary server. Exiting..")
            exit()

    def set_primary(self):
        servers = [(name, uri) for name, uri in self.ns.list(prefix="just_hungry.back_end").items()]
        for s in servers:
            active = Pyro4.Proxy(s[1])
            try:
                active._pyroBind()
            except Exception as e:
                continue
            if active.ping_respond():
                self.primary = active
                self.primary.promote_master()
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

    def ping_primary(self):
        try:
            self.primary._pyroBind()
            if self.primary.ping_respond():
                return True
        except Exception as e:
            return False
        return False

    def forward_request(self, method, **args):
        VALID_METHODS = set(["login", "logout", "create_account", "delete_account", "make_order", "cancel_order", "view_orders", "show_items"])

        if not method in VALID_METHODS:
            print("ERROR: Unknown method!")
            return False

        if not self.ping_primary():
            print("ERROR: Current primary is down! Finding new server..")
            if not self.set_primary():
                print("ERROR: Failed to find new primary server!")
                return False
        server_result = self.methods[method](**args)
        self.primary.master_sync()
        return server_result

sys.excepthook = Pyro4.util.excepthook

if __name__ == "__main__":
    Pyro4.Daemon.serveSimple({
            FrontServer: "just_hungry.front_end"
        }, ns=True)

