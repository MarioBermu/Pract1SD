from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import re
# Clase que maneja las solicitudes XML-RPC
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Lista de insultos prohibidos
insults = ["idiota", "torpe", "patán", "zoquete", "burro", "cabezón", "menso", "necio"]

# Lista donde se almacenarán los textos filtrados
filtered_texts = []

def filter_text(text):
    """Filtra los insultos en el texto y los reemplaza por 'CENSORED'"""
    pattern = r'\b(' + '|'.join(insults) + r')\b'  # Expresión regular para detectar palabras exactas
    filtered_text = re.sub(pattern, 'CENSORED', text, flags=re.IGNORECASE)
    filtered_texts.append(filtered_text)
    return filtered_text

def get_filtered_texts():
    """Devuelve la lista completa de textos filtrados"""
    return filtered_texts

# Configurar el servidor XML-RPC
server = SimpleXMLRPCServer(("localhost", 8001), requestHandler=RequestHandler, allow_none=True)
print("InsultFilterService is running on port 8001...")

# Registrar funciones en el servidor
server.register_function(filter_text, "filter_text")
server.register_function(get_filtered_texts, "get_filtered_texts")

# Mantener el servidor en ejecución
server.serve_forever()
