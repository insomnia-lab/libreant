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
        from gevent import version_info

        logger = app._logger
        port = int(app.config.get('PORT', 5000))
        address = app.config.get('ADDRESS', '')
        logger.info('Listening on http://{}:{}/'.format(address or '0.0.0.0', port))
        server_params = dict()
        #starting from gevent version 1.1b1 we can pass custom logger to gevent
        if version_info[:2] >= (1,1):
            server_params['log'] = logger
        http_server = WSGIServer((address, port), run_app, **server_params)
        http_server.serve_forever()

    if app.config['DEBUG']:
        from werkzeug._reloader import run_with_reloader
        run_with_reloader(run_server)
    else:
        run_server()
