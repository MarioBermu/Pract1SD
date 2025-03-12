from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler) as server:
    server.register_introspection_functions()

    insults = ["Eres más inútil que el 'uepa' en un mensaje de texto.",
                "Tienes menos futuro que un pez en el desierto.",
                "Si fueras más lento, irías hacia atrás."
                ]  # List to store insults

    # Function to add an insult to the list
    def add_insult(insult):
        insults.append(insult)
        return f"Insult added: {insult}"

    # Function to get the list of insults
    def get_insults():
        return insults

    # Function to return a random insult
    def insult_me():
        if insults:
            return random.choice(insults)
        else:
            return "No insults available. Add some first!"

    # Register functions with the server
    server.register_function(add_insult, 'add_insult')
    server.register_function(get_insults, 'get_insults')
    server.register_function(insult_me, 'insult_me')

    # Run the server's main loop
    server.serve_forever()