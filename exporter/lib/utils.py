#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import logging
import inspect
import time

log = logging.getLogger(__package__)


def short_msg(msg, chars=75):
    """ Truncates the message to {chars} characters and adds three dots at the end """
    return (str(msg)[:chars] + '..') if len(str(msg)) > chars else str(msg)


def DDoSProtectionHandler(error, sleep=1):
    """ Prints a warning and sleeps """
    caller = inspect.stack()[1].function
    log.warning(f'({caller}) Rate limit has been reached. Sleeping for {sleep}s. The exception: {short_msg(error)}')
    time.sleep(sleep)  # don't hit the rate limit


def ExchangeNotAvailableHandler(error, sleep=10):
    """ Prints an error and sleeps """
    caller = inspect.stack()[1].function
    log.error(f'({caller}) The exchange API could not be reached. Sleeping for {sleep}s. The error: {short_msg(error)}')
    time.sleep(sleep)  # don't hit the rate limit


def AuthenticationErrorHandler(error, nonce=''):
    """ Logs hints about the authentication error """
    caller = inspect.stack()[1].function
    error = short_msg(error)
    message = f"({caller}) Can't authenticate to read the accounts."
    if 'request timestamp expired' in str(error):
        if nonce == 'milliseconds':
            message += ' Set NONCE to `seconds` and try again.'
        elif nonce == 'seconds':
            message += ' Set NONCE to `milliseconds` and try again.'
    else:
        message += f' Check your API_KEY/API_SECRET/API_UID/API_PASS. Disabling the credentials. The exception: {error}'
    log.error(message)


def PermissionDeniedHandler(error):
    """ Prints error and gives hints about the cause """
    caller = inspect.stack()[1].function
    error = short_msg(error)
    log.error(f'({caller}) The exchange reports "permission denied": {error} Check the API token permissions')
