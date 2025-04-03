from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
from socketserver import ThreadingMixIn

# Clase que maneja las solicitudes XML-RPC
class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista donde se almacenarán los insultos
insult_list = []

def store_insult(insult):
    """Almacena un insulto si no está en la lista"""
    print(f"[XML-RPC] Storing insult: {insult}")
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
#server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
server = ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)

print("InsultService is running on port 8000...")

# Registrar funciones en el servidor
server.register_function(store_insult, "store_insult")
server.register_function(get_insult_list, "get_insult_list")
server.register_function(get_random_insult, "get_random_insult")

# Mantener el servidor en ejecución
server.serve_forever()
