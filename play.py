

import code
import rlcompleter
import sys
import threading

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
    - set_sender()  # Set sender
    - states  # View all states
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
    """, local=func.namespace)
