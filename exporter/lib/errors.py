#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" crypto-exporter Custom Errors """


class Error(Exception):
    """ The base class """


class EnvironmentMissing(Error):
    """ Raised when an environment variable is missing """
