# -*- Encoding: utf-8 -*-
"""log in 4 files"""
import logging
import os


DEFAULT_LOG_LEVEL = logging.DEBUG


def get_4f_logger(formatter, path, name=''):
    log = logging.getLogger(name)
    log.setLevel(DEFAULT_LOG_LEVEL)

    if not os.path.exists(path):
        os.makedirs(path)

    lvls = ['debug', 'info', 'warn', 'error']

    for lvl in lvls:
        logfile = os.path.join(path, '{}.log'.format(lvl.lower()))
        hdlr = logging.FileHandler(logfile)
        hdlr.setLevel(getattr(logging, lvl.upper()))
        hdlr.setFormatter(formatter)
        log.addHandler(hdlr)
    return log


def debug_logger(log_dir='log', logger_name='debug'):
    log_format = ('%(asctime)s|%(levelname)s|%(message)s'
                  '|%(filename)s-%(lineno)s')
    return get_4f_logger(logging.Formatter(log_format), log_dir, logger_name)


if __name__ == '__main__':
    log = debug_logger()
    log.error('test log')
    log.info('info log')
