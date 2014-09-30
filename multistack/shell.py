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

from __future__ import absolute_import
from __future__ import print_function

import argparse
import getpass
import os
import sys
from . import utils
from . import config
from . import credentials


class MultiShell(object):

    def __init__(self, multiclient):
        self.multiclient = multiclient()

    def check_environment_presets(self):
        """
        Checks for environment variables that can cause problems with multistack
        """
        prefix_tuple = tuple([x.upper() for x in self.multiclient.prefix_list])
        presets = [x for x in os.environ.copy().keys() if x.startswith(
            prefix_tuple)]
        if len(presets) > 0:
            utils.print_error("Found existing environment variables that may "
                              "cause conflicts:", title='Warning', exit=False)
            for preset in presets:
                print("  - %s" % preset)

    def run_client(self):
        self.check_environment_presets()
        valid_envs = sorted(self.multiclient.available_envs)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-l', '--list', action=utils._ListAction,
                                 dest='listenvs',
                                 client_config=self.multiclient.client_config,
                                 help='list all configured environments')
        self.parser.add_argument('-x', '--executable',
                                 help='command to run instead of '
                                      '%s' %
                                      self.multiclient.default_executable)
        self.parser.add_argument('-d', '--debug', action='store_true',
                                 help='show client\'s debug output')
        self.parser.add_argument('env',
                                 help='environment to run the client against.',
                                 choices=valid_envs)
        multistack_args, client_args = self.parser.parse_known_args()
        if not client_args:
            error = 'No arguments were provided to pass along to the client.'
            utils.print_error(error, title='Missing client arguments')
        try:
            self.multiclient.client_env = multistack_args.env
            returncode = self.multiclient.run_client(client_args,
                                                     multistack_args)
            sys.exit(returncode)
        except AttributeError as e:
            utils.print_error(e)


class MultiKeyringShell(object):

    def __init__(self):
        self.client_config = config.load_multistack_config()

    def get_password(self, parameter, env_list):
        parameter = parameter.upper()
        utils.print_error(
            """If this operation is successful, the %s credentials stored
for the following environments will be displayed in your terminal as plain text.
""" % parameter, title='Warning', exit=False)
        print('  - Environments : %s' % '\n                   '.join(env_list))
        print('  - Parameter    : %s' % parameter)
        print('\nIf you really want to proceed, type yes and press enter:')
        try:
            if sys.version_info.major >= 3:
                confirm = input('')
            else:
                confirm = raw_input('')
        except KeyboardInterrupt:
            print('')
            confirm = ''
        if confirm != 'yes':
            error = 'Your keyring was not read or altered.'
            utils.print_error(error, title='Canceled')
        print()
        for env in env_list:
            try:
                password = credentials.password_get(env, parameter)
            except:
                password = None
            if password:
                msg = '%s->%s: %s' % (env, parameter, password.decode('utf-8'))
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (env, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print
        utils.print_notice(
            """If you encountered a failure getting your credentials then there
are likely no credentials stored for that environment/parameter combination.
""", title='Complete')

    def delete_password(self, parameter, env_list):
        parameter = parameter.upper()
        utils.print_notice('Preparing to delete a password in the keyring '
                           'for:', title='Keyring operation')
        print('  - Environments : %s' % '\n                   '.join(env_list))
        print('  - Parameter    : %s' % parameter)
        print('\nIf you really want to proceed, type yes and press enter:')
        try:
            if sys.version_info.major >= 3:
                confirm = input('')
            else:
                confirm = raw_input('')
        except KeyboardInterrupt:
            print('')
            confirm = ''
        if confirm != 'yes':
            error = 'Your keyring was not read or altered.'
            utils.print_error(error, title='Canceled')
        print()
        for env in env_list:
            try:
                delete_ok = credentials.password_delete(env, parameter)
            except:
                delete_ok = False
            if delete_ok:
                msg = '%s->%s' % (env, parameter)
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (env, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print()
        utils.print_notice(
            """If you encountered a failure deleting your credentials then you
should check your keyring configuration.
""", title='Complete')

    def set_password(self, parameter, env_list):
        parameter = parameter.upper()
        utils.print_notice('Preparing to set a password in the keyring for:',
                           title='Keyring operation')
        print('  - Environments : %s' % '\n                   '.join(env_list))
        print('  - Parameter    : %s' % parameter)
        print('\nIf this is correct, enter the corresponding credential '
              'to store in \nyour keyring or press CTRL-D to abort:')
        # Prompt for a password and catch a CTRL-D
        try:
            password = getpass.getpass('')
        except:
            password = None
            print()
        print()
        # Did we get a password from the prompt?
        if not password or len(password) < 1:
            utils.print_error('Your keyring was not read or altered.',
                              title='Canceled')
        for env in env_list:
            # Try to store the password
            try:
                store_ok = credentials.password_set(env, parameter, password)
            except:
                store_ok = False
            if store_ok:
                msg = '%s->%s' % (env, parameter)
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (env, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print()
        utils.print_notice(
            """If you encountered a failure setting your credentials then you
should check your keyring configuration.
""", title='Complete')

    def run_keyring(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-l', '--list', action=utils._ListAction,
                                 dest='listenvs',
                                 client_config=self.client_config,
                                 help='list all configured environments')
        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-g', '--get', action='store_true',
                           dest='get_password',
                           help='retrieves credentials from keychain storage')
        group.add_argument('-s', '--set', action='store_true',
                           dest='set_password',
                           help='stores credentials in keychain storage')
        group.add_argument('-d', '--delete', action='store_true',
                           dest='delete_password',
                           help='deletes credentials in keychain storage')
        self.parser.add_argument('env',
                                 help='environment to set parameter in',
                                 nargs='+')
        self.parser.add_argument('parameter',
                                 help='parameter to set')
        args = self.parser.parse_args()
        if args.get_password:
            self.get_password(args.parameter, sorted(args.env))
        if args.set_password:
            self.set_password(args.parameter, sorted(args.env))
        if args.delete_password:
            self.delete_password(args.parameter, sorted(args.env))


def main_keyring():
    multikeyring_shell = MultiKeyringShell()
    multikeyring_shell.run_keyring()
