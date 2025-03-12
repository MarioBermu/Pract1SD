import Pyro4

@Pyro4.expose
class MyRemoteObject:
    def greet(self, name):
        return f"Hello, {name}!"

    def add(self, a, b):
        return a + b

# Iniciar el servidor y registrar el objeto
def start_server():
    daemon = Pyro4.Daemon()  # Crear el servidor Pyro
    ns = Pyro4.locateNS()  # Conectarse al Name Server
    uri = daemon.register(MyRemoteObject())  # Registrar el objeto
    ns.register("example.remote.object", uri)  # Publicarlo en el Name Server
    print(f"MyRemoteObject running at {uri}")  
    daemon.requestLoop()  # Mantener el servidor activo

if __name__ == "__main__":
    start_server()
