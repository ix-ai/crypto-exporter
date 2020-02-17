#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Handles the exchange data and communication """

import logging
import inspect
import time
import os
import json
from distutils.util import strtobool
from . import errors


log = logging.getLogger('crypto-exporter')


def short_msg(msg, chars=75):
    """ Truncates the message to {chars} characters and adds three dots at the end """
    return (str(msg)[:chars] + '..') if len(str(msg)) > chars else str(msg)


def ddos_protection_handler(error, sleep=1, shortify=True):
    """ Prints a warning and sleeps """
    caller = inspect.stack()[1].function
    if shortify:
        error = short_msg(error)
    log.warning(f'({caller}) Rate limit has been reached. Sleeping for {sleep}s. The exception: {error}')
    time.sleep(sleep)  # don't hit the rate limit


def exchange_not_available_handler(error, sleep=10, shortify=True):
    """ Prints an error and sleeps """
    caller = inspect.stack()[1].function
    if shortify:
        error = short_msg(error)
    log.error(f'({caller}) The exchange API could not be reached. Sleeping for {sleep}s. The error: {error}')
    time.sleep(sleep)  # don't hit the rate limit


def authentication_error_handler(error, nonce='', shortify=True):
    """ Logs hints about the authentication error """
    caller = inspect.stack()[1].function
    if shortify:
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


def permission_denied_handler(error, shortify=True):
    """ Prints error and gives hints about the cause """
    caller = inspect.stack()[1].function
    if shortify:
        error = short_msg(error)
    log.error(f'({caller}) The exchange reports "permission denied": {error} Check the API token permissions')


def generic_error_handler(error, shortify=True):
    """ Handler for generic errors """
    caller = inspect.stack()[1].function
    if shortify:
        error = short_msg(error)
    log.error(f'({caller}) A generic error occurred: {error}')


def gather_environ(keys=None) -> dict:
    """
    Return a dict of environment variables correlating to the keys dict

    :param keys: The environ keys to use, each of them correlating to `int`, `list`, `json`, `string` or `bool`.
                 The format of the values should be key = {'key_type': type, 'default': value, 'mandatory': bool}
    :return: A dict of found environ values
    """
    environs = {}
    for key, key_details in keys.items():
        environment_key = os.environ.get(key.upper())
        if environment_key:
            environs.update({key: environment_key})

            if key_details['key_type'] == 'int':
                environs[key] = int(environment_key)

            if key_details['key_type'] == 'list':
                environs[key] = environs[key].split(',')

            if key_details['key_type'] == 'json':
                try:
                    environs[key] = json.loads(environment_key)
                except (TypeError, json.decoder.JSONDecodeError):
                    log.warning((
                        f"{key.upper()} does not contain a valid JSON object."
                        f" Setting to: {key_details['default']}."
                    ))
                    environs[key] = key_details['default']

            if key_details['key_type'] == 'bool':
                try:
                    environs[key] = strtobool(environment_key)
                except ValueError:
                    log.warning(f"Invalid value for {key.upper()}. Setting to: {key_details['default']}.")
                    environs[key] = key_details['default']

            if key_details.get('redact'):
                log.debug(f"{key.upper()} set to ***REDACTED***")
            else:
                log.debug(f"{key.upper()} set to {environs[key]}")

        elif key_details['mandatory']:
            raise errors.EnvironmentMissing(f'{key.upper()} is mandatory')
        else:
            environs[key] = key_details['default']
            log.debug(f"{key.upper()} is not set. Using default: {key_details['default']}")
    return environs
