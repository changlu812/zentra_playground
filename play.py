

import code
import rlcompleter
import sys
import threading

import tornado.web
import tornado.ioloop

import importlib.util
import importlib.machinery
import os
import hashlib
import string
import json
import binascii
try:
    from eth_utils import keccak
except ImportError:
    keccak = None

import space
import rpc


class NamedFunction:
    def __init__(self, f, name):
        self.f = f
        self.name = name

    def __call__(self, *args):
        a = list(args)
        if space.sender is None:
            raise Exception('sender is not set')
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

def load_all_zips():
    funcs_dir = os.path.join(os.path.dirname(__file__), 'funcs')
    if not os.path.exists(funcs_dir):
        print(f"Warning: {funcs_dir} not found.")
        return
    for filename in os.listdir(funcs_dir):
        if not filename.endswith('.py') or filename == '__init__.py':
            continue
        logic_path = os.path.join(funcs_dir, filename)
        module_name = f'funcs_{filename[:-3]}'
        loader = importlib.machinery.SourceFileLoader(module_name, logic_path)
        spec = importlib.util.spec_from_loader(module_name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)

        mod.get = space.get
        mod.put = space.put
        mod.event = space.event
        mod.handle_lookup = space.handle_lookup
        mod.hashlib = hashlib
        mod.string = string
        mod.json = json
        mod.binascii = binascii
        if keccak:
            mod.keccak = keccak

        for attr in dir(mod):
            if attr in ['put', 'get', 'event', 'handle_lookup']:
                continue
            if attr.startswith('_'):
                continue
            func = getattr(mod, attr)
            if callable(func):
                # print(attr)
                wrapped = NamedFunction(func, attr)
                namespace[attr] = wrapped

load_all_zips()


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
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        # (r"/state", StateHandler),
        (r"/", rpc.RPCHandler),
        # (r'/api/get_latest_state', GetLatestStateAPIHandler),
        # (r'/api/query_recent_state', QueryRecentStateAPIHandler),
    ])
    app.listen(8545)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # Thread will close when main program exits
    server_thread.start()

    code.interact(banner="""
    Zentra Interactive python console
    Available commands:
    - put(owner, asset, var, value, key=None)  # Store state
    - get(asset, var, default=None, key=None)  # Access state
    - blocknumber()  # Current block number
    - nextblock()  # Start next block
    - states  # View all states
    - set_sender()  # Set sender
    - sender  # View sender

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
