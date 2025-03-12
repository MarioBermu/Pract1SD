from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Subscriber Server Code
def start_subscriber(port):
    with SimpleXMLRPCServer(('localhost', port), requestHandler=RequestHandler) as subscriber_server:
        subscriber_server.register_introspection_functions()

        class Subscriber:
            def notify(self, insult):
                print(f"Subscriber on port {port} received insult: {insult}")
                return True

        subscriber_server.register_instance(Subscriber())
        print(f"Subscriber running on port {port}...")
        subscriber_server.serve_forever()

# Start 3 subscriber servers in separate threads
for port in [8001, 8002, 8003]:
    threading.Thread(target=start_subscriber, args=(port,), daemon=True).start()

# Keep the main thread alive
import time
while True:
    time.sleep(1)
