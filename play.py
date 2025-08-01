

import code
# import readline
import rlcompleter
import sys
import threading

import tornado.web
import tornado.ioloop

import space
import funcs
import rpc

class NamedFunction:
    def __init__(self, f, name):
        self.f = f
        self.name = name

    def __call__(self, *args):
        a = list(args)
        r = self.f({'sender': space.sender}, {'p': 'zen', 'a': a, 'f': self.name})
        space.nextblock()
        return r

    def __str__(self):
        return self.f.__str__()

    def __repr__(self):
        return self.f.__repr__()

def get_block_number():
    return len(space.states)

def set_sender(sender):
    space.sender = sender
    namespace['sender'] = space.sender

# Create custom namespace with imported functions
namespace = {
    'put': space.put,
    'get': space.get, 
    'states': space.states,
    'blocknumber': get_block_number,
    'nextblock': space.nextblock,
    'sender': space.sender,
    'set_sender': set_sender,
    '__name__': '__console__',
    '__doc__': None,
}

funcs_built = {'__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', '__builtins__', 'string', 'put', 'get', 'handle_lookup'}
for func in dir(funcs):
    if func not in funcs_built:
        # print(type(func), funcs.__dict__[func])
        f = NamedFunction(funcs.__dict__[func], func)
        namespace[func] = f


# class StateHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.write(json.dumps({
#             'grid': game_state.grid,
#             'score': game_state.score,
#             'game_over': game_state.game_over
#         }))

# class ActionHandler(tornado.web.RequestHandler):
#     def post(self):
#         direction = self.get_argument('move')
#         game.move(direction)

def start_server():
    app = tornado.web.Application([
        # (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        # (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        # (r"/state", StateHandler),
        (r"/", rpc.RPCHandler),
        # (r'/api/get_latest_state', GetLatestStateAPIHandler),
        # (r'/api/query_recent_state', QueryRecentStateAPIHandler),
    ])
    app.listen(8545)
    tornado.ioloop.IOLoop.current().start()


server_thread = threading.Thread(target=start_server)
server_thread.daemon = True  # Thread will close when main program exits
server_thread.start()


# Enable tab completion
# readline.parse_and_bind("tab: complete")

# Create and start interactive console
# console = code.InteractiveConsole(namespace)
code.interact(banner="""
Zentra Interactive python console
Available commands:
- put(owner, asset, var, value, key=None)  # Store state
- get(asset, var, default=None, key=None)  # Get state
- blocknumber()  # Current block number
- states  # View all states
- set_sender()  # Current sender
- sender  # Current sender

Example:
>>> put('alice', 'USDC', 'balance', 100, 'alice')
>>> get('USDC', 'balance', 0, 'alice')
100
>>> states
[{'asset-balance': {'alice': 100}}]
>>> nextblock()
>>> asset_create('USDC')
Ok, let's start!
""", local=namespace)
