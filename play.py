

import code
import rlcompleter
import sys
import threading
try:
    import readline
except:
    pass

import tornado.web
import tornado.ioloop

try:
    from eth_utils import keccak
except ImportError:
    keccak = None

import space
import rpc
import func


func.load_all_zips()

GLOBAL_FUNCTIONS = func.namespace


class GetLatestStateAPIHandler(tornado.web.RequestHandler):
    def get(self):
        prefix = self.get_argument('prefix')
        print(prefix)
        prefix = prefix.split('-')
        asset = prefix[1]
        if ':' in prefix[2]:
            var, key = prefix[2].split(':')
            value, owner = space.get(asset, var, None, key)
        else:
            var = prefix[2]
            key = None
            value, owner = space.get(asset, var, None)
        print(value)
        self.finish({'result': value})

class QueryRecentStateAPIHandler(tornado.web.RequestHandler):
    def get(self):
        prefix = self.get_argument('prefix')
        print(prefix)


class EventsAPIHandler(tornado.web.RequestHandler):
    def get(self):
        txhash = self.get_argument('txhash')
        print(txhash)
        self.finish({'result': []})

def start_server():
    app = tornado.web.Application([
        # (r'/(favicon\.ico)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static/'}),
        # (r"/state", StateHandler),
        (r"/", rpc.RPCHandler),
        (r'/api/get_latest_state', GetLatestStateAPIHandler),
        (r'/api/query_recent_state', QueryRecentStateAPIHandler),
        (r'/api/events', EventsAPIHandler),
    ])
    app.listen(8545)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True  # Thread will close when main program exits
    server_thread.start()
    try:
        readline.parse_and_bind("tab: complete")
    except:
        pass

    code.interact(banner="""
    Zentra Interactive python console
    Available commands:
    - put(owner, asset, var, value, key=None)  # Store state
    - get(asset, var, default=None, key=None)  # Access state
    - blocknumber()  # Current block number
    - nextblock()  # Start next block
    - setsender()  # Set sender
    - states  # View all states
    - sender  # Current sender

    Example:
    >>> put('alice', 'USDC', 'balance', 100, 'alice')
    >>> get('USDC', 'balance', 0, 'alice')
    100
    >>> states
    [{'asset-balance': {'alice': 100}}]
    >>> nextblock()
    >>> setsender(a[0])
    >>> asset_create('USDC')
    Ok, let's start!
    """, local=func.namespace)

