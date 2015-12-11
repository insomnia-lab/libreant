'''
This module provides some function to make running a webserver a little easier
'''


def gevent_run(app):
    from gevent.wsgi import WSGIServer
    import gevent.monkey
    from werkzeug.debug import DebuggedApplication
    gevent.monkey.patch_socket()
    run_app = app
    if app.config['DEBUG']:
        run_app = DebuggedApplication(app)

    def run_server():
        import logging
        port = int(app.config.get('PORT', 5000))
        address = app.config.get('ADDRESS', '')
        logging.getLogger('webant').info('Listening on http://{}:{}/'.format(address or '0.0.0.0', port))
        http_server = WSGIServer((address, port), run_app)
        http_server.serve_forever()

    if app.config['DEBUG']:
        from werkzeug._reloader import run_with_reloader
        run_with_reloader(run_server)
    else:
        run_server()
