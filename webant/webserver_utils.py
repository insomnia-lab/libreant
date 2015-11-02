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
        port = int(app.config.get('PORT', 5000))
        address = app.config.get('ADDRESS', '')
        print('Listening on http://%s:%d/' % (address or '0.0.0.0', port))
        http_server = WSGIServer((address, port), run_app)
        http_server.serve_forever()

    if app.config['DEBUG']:
        from werkzeug.serving import run_with_reloader
        run_with_reloader(run_server)
    else:
        run_server()
