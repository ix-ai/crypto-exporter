#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Global logging configuration """

import logging
import pygelf


def setup_logger(name, level='INFO', gelf_host=None, gelf_port=None, **kwargs):
    """ sets up the logger """
    logging.basicConfig(handlers=[logging.NullHandler()])
    formatter = logging.Formatter(
        fmt='%(asctime)s.%(msecs)03d %(levelname)s [%(module)s.%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if gelf_host and gelf_port:
        handler = pygelf.GelfUdpHandler(
            host=gelf_host,
            port=gelf_port,
            debug=True,
            include_extra_fields=True,
            **kwargs
        )
        logger.addHandler(handler)

    return logger
