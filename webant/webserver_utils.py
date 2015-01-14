'''
This module provides some function to make running a webserver a little easier
'''


def gevent_run(app):
    from gevent.wsgi import WSGIServer
    import gevent.monkey
    from werkzeug.debug import DebuggedApplication
    from werkzeug.serving import run_with_reloader
    gevent.monkey.patch_socket()
    if app.config['DEBUG']:
        app = DebuggedApplication(app)

    @run_with_reloader
    def run_server():
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
