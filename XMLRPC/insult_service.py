from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
from socketserver import ThreadingMixIn
import sys
import json
import os

SERVER_LIST_FILE = "active_servers.json"
request_count = 0


def register_server(port):
    """Registra el puerto del servidor en el archivo JSON"""
    if os.path.exists(SERVER_LIST_FILE):
        with open(SERVER_LIST_FILE, "r") as file:
            try:
                servers = json.load(file)
            except json.JSONDecodeError:
                servers = []
    else:
        servers = []

    if port not in servers:
        servers.append(port)

    with open(SERVER_LIST_FILE, "w") as file:
        json.dump(servers, file)

# Antes de iniciar el servidor, regístralo
port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000 
register_server(port)


# Clase que maneja las solicitudes XML-RPC
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista donde se almacenarán los insultos
insult_list = []

def store_insult(insult):
    """Almacena un insulto si no está en la lista"""
    #print(f"[XML-RPC] Storing insult: {insult}")
    global request_count
    request_count += 1
    print(f"[XML-RPC:{port}] Peticiones recibidas: {request_count}")
    if insult not in insult_list:
        insult_list.append(insult)
        return f"Stored new insult: {insult}"
    return f"Duplicate insult ignored: {insult}"

def get_insult_list():
    """Devuelve la lista completa de insultos"""
    return insult_list

def get_random_insult():
    """Devuelve insulto random"""
    return random.choice(insult_list)

# Configurar el servidor XML-RPC
#port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
#server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
server = ThreadedXMLRPCServer(("localhost", port), requestHandler=RequestHandler, allow_none=True)

print(f"InsultService is running on port {port}...")

# Registrar funciones en el servidor
server.register_function(store_insult, "store_insult")
server.register_function(get_insult_list, "get_insult_list")
server.register_function(get_random_insult, "get_random_insult")

# Mantener el servidor en ejecución
server.serve_forever()
