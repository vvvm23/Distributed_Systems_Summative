import Pyro4

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class FrontServer:
    def __init__:
        pass

if __name__ == "__main__":
    Pyro4.Daemon.serveSimple({
            FrontServer: "example.front_server"
        }, ns=True)
