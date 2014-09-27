#!/usr/bin/env python
#
# Copyright 2014 M. David Bennett
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

from __future__ import print_function

import sys
import argparse


class _ListAction(argparse._HelpAction):
    """ListAction used for the -l and --list arguments."""
    SUPPRESS = '==SUPPRESS=='

    def __init__(self, option_strings, dest=SUPPRESS, default=SUPPRESS,
                 client_config=None, help=None):
        super(argparse._HelpAction, self).__init__(
            option_strings=option_strings, dest=dest, default=default, nargs=0,
            help=help)
        self.environments = {}
        for environment in client_config.sections():
            self.environments[environment] = client_config.items(environment)

    def __call__(self, parser, *args, **kwargs):
        for env, config in self.environments.items():
            envheader = '-- %s ' % gwrap(env)
            print(envheader.ljust(86, '-'))
            for param, value in sorted(config):
                print('  %s: %s' % (param.upper().ljust(21), value))
        parser.exit()


def gwrap(some_string):
    """
    Returns green text
    """
    return "\033[92m%s\033[0m" % some_string


def rwrap(some_string):
    """
    Returns red text
    """
    return "\033[91m%s\033[0m" % some_string


def print_error(error, title=None, exit=True):
    if not title:
        title = "Something broke"
    print("[%s] %s" % (rwrap(title), error))
    if exit:
        sys.exit(1)


def print_notice(msg, title=None):
    if not title:
        title = "Notice"
    print("[%s] %s" % (gwrap(title), msg))
