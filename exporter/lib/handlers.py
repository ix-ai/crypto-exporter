#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Various exception handlers """
import time
from .log import ExporterLogging as log


def DDoSProtectionHandler(error, sleep=1):
    """ Prints a warning and sleeps """
    log.LOG.warning('Rate limit has been reached. Sleeping for {}s. The exception: {}'.format(sleep, error))
    time.sleep(sleep)  # don't hit the rate limit


def ExchangeNotAvailableHandler(error, sleep=10):
    """ Prints an error and sleeps """
    log.LOG.error('The exchange API could not be reached. Sleeping for {}. The error: {}'.format(sleep, error))
    time.sleep(sleep)  # don't hit the rate limit


def AuthenticationErrorHandler(error, nonce=''):
    """ Logs hints about the authentication error """
    log.LOG.error("Can't authenticate to read the accounts")
    if 'request timestamp expired' in str(error):
        if nonce == 'milliseconds':
            log.LOG.error('Set NONCE to `seconds` and try again')
        elif nonce == 'seconds':
            log.LOG.error('Set NONCE to `milliseconds` and try again')
    else:
        log.LOG.error('{} The exception: {}'.format(
            "Check your API_KEY/API_SECRET/API_UID. Disabling the credentials.",
            str(error)
        ))


def PermissionDeniedHandler(error):
    """ Prints error and gives hints about the cause """
    log.LOG.error('The exchange reports "permission denied": {}'.format(error))
    log.LOG.error('Check the API token permissions')