import sys
import Pyro4
import Pyro4.util

def valid_server(uri):
    try:
        s = Pyro4.Proxy(uri)
        s._pyroBind()
    except Exception as e:
        return False
    return True

sys.excepthook = Pyro4.util.excepthook
if __name__ == '__main__':
    ns = Pyro4.locateNS()
    
    GREEN = "\033[42m" 
    RED = "\033[41m"
    END = "\033[0m"

    while True:
        servers = [(name, uri) for name, uri in ns.list(prefix="just_hungry.back_end").items() if valid_server(uri)]

        print('\n'.join(f"{i+1}:\t{x[0]} \t{x[1]}\t{GREEN+'UP'+END if Pyro4.Proxy(x[1]).ping_respond() else RED+'DOWN'+END}" for i, x in enumerate(servers) ))
        print("0.\tExit")
        x = int(input())
        if x == 0:
            break
        if x > 0 and x <= len(servers):
            Pyro4.Proxy(servers[x-1][1]).toggle_status()


