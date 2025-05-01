from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import re
from socketserver import ThreadingMixIn
import sys
import json
import os

SERVER_LIST_FILE = "active_servers_filter.json"
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

# Lista de insultos prohibidos
insults = ["idiota", "torpe", "patán", "zoquete", "burro", "cabezón", "menso", "necio","tonto"]

# Lista donde se almacenarán los textos filtrados
filtered_texts = []

def filter_text(text):
    """Filtra los insultos en el texto y los reemplaza por 'CENSORED'"""
    global request_count
    request_count += 1
    print(f"[XML-RPC FILTER:{port}] Peticiones recibidas: {request_count}")
    
    pattern = r'\b(' + '|'.join(insults) + r')\b'  # Expresión regular para detectar palabras exactas
    filtered_text = re.sub(pattern, 'CENSORED', text, flags=re.IGNORECASE)
    filtered_texts.append(filtered_text)
    return filtered_text

def get_filtered_texts():
    """Devuelve la lista completa de textos filtrados"""
    return filtered_texts

# Configurar el servidor XML-RPC
#port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
server = ThreadedXMLRPCServer(("localhost", port), requestHandler=RequestHandler, allow_none=True)
#server = SimpleXMLRPCServer(("localhost", 8001), requestHandler=RequestHandler, allow_none=True)
print(f"InsultFilterService is running on port {port}...")

# Registrar funciones en el servidor
server.register_function(filter_text, "filter_text")
server.register_function(get_filtered_texts, "get_filtered_texts")

# Mantener el servidor en ejecución
server.serve_forever()
