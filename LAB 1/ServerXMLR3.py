from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import random

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create Insult Server
class InsultServer:
    def __init__(self):
        self.insults = []
        self.subscribers = []

    def add_insult(self, insult):
        self.insults.append(insult)
        self.notify_subscribers(insult)
        return f"Insult added: {insult}"

    def get_insults(self):
        return self.insults

    def insult_me(self):
        if self.insults:
            return random.choice(self.insults)
        else:
            return "No insults available. Add some first!"

    def add_subscriber(self, subscriber_url):
        self.subscribers.append(subscriber_url)
        return f"Subscriber added: {subscriber_url}"

    def notify_subscribers(self, insult):
        for subscriber_url in self.subscribers:
            try:
                subscriber = xmlrpc.client.ServerProxy(subscriber_url)
                subscriber.notify(insult)
            except Exception as e:
                print(f"Failed to notify {subscriber_url}: {e}")

# Start the Insult Server
with SimpleXMLRPCServer(('localhost', 8000), requestHandler=RequestHandler) as server:
    server.register_introspection_functions()
    insult_service = InsultServer()
    server.register_instance(insult_service)
    print("Insult Server running on port 8000...")
    server.serve_forever()
