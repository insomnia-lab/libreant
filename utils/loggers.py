import logging


LOG_NAMES = ['webant', 'fsdb', 'presets', 'agherant', 'config_utils', 'libreantdb', 'archivant', 'users']


def initLoggers(logLevel=logging.WARNING, logNames=LOG_NAMES):
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
    streamHandler.setFormatter(formatter)
    loggers = map(logging.getLogger, logNames)
    for logger in loggers:
        logger.setLevel(logLevel)
        if not logger.handlers:
            logger.addHandler(streamHandler)
