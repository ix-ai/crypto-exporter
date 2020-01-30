#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Initializes the logging """
import logging
import os
import sys
import pygelf


class ExporterLogging():  # pylint: disable=too-few-public-methods
    """ Configures the logging for the app """
    FILENAME = os.path.splitext(sys.modules['__main__'].__file__)[0]
    GELF_ENABLED = False
    LOG = logging.getLogger(__name__)
    logging.basicConfig(
        stream=sys.stdout,
        level=os.environ.get("LOGLEVEL", "WARNING"),
        format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if os.environ.get('GELF_HOST') and not GELF_ENABLED:
        GELF = pygelf.GelfUdpHandler(
            host=os.environ.get('GELF_HOST'),
            port=int(os.environ.get('GELF_PORT', 12201)),
            debug=True,
            include_extra_fields=True,
            _exchange=os.environ.get('EXCHANGE', 'unconfigured'),
            _ix_id=os.environ.get('EXCHANGE', FILENAME),
        )
        LOG.addHandler(GELF)
        GELF_ENABLED = True

    LOG.info('Initialized logging with GELF enabled: {}'.format(GELF_ENABLED))
