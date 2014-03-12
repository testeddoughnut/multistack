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


import getpass
import argparse
import client
import utils


class MultiShell(object):

    def __init__(self):
        self.executable = None
        self.multiclient = client.MultiClient()
        self.setup_base_args()

    def set_client_env(self, new_env):
        try:
            self.multiclient.set_client_env(new_env)
        except Exception as e:
            utils.print_error(e)

    def get_password(self, parameter, env_list):
        error = ('If this operation is successful, the \'%s\' credentials '
                 'stored \nfor the following environments will be displayed'
                 ' in your terminal as plain text.' % parameter)
        utils.print_error(error, title='Warning', exit=False)
        print '  - Environments : %s' % '\n                    '.join(env_list)
        print '  - Parameter    : %s' % parameter
        print '\nIf you really want to proceed, type yes and press enter:',
        try:
            confirm = raw_input('')
        except:
            confirm = "no"
            print
        if confirm != 'yes':
            error = 'Your keyring was not read or altered.'
            utils.print_error(error, title='Canceled')
        print
        for environment in env_list:
            username = '%s:%s' % (environment, parameter)
            try:
                password = self.multiclient.password_get(username, parameter)
            except:
                password = None
            if password:
                msg = '%s->%s: %s' % (environment, parameter, password)
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (environment, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print
        utils.print_notice('If you encountered a failure retrieving the '
                           'credentials then there\nare likely no credentials '
                           'stored for that environment/parameter '
                           'combination.', title='Complete')

    def delete_password(self, parameter, env_list):
        utils.print_notice('Preparing to delete a password in the keyring '
                           'for:', title='Keyring operation')
        print '  - Environments : %s' % '\n                    '.join(env_list)
        print '  - Parameter    : %s' % parameter
        print '\nIf you really want to proceed, type yes and press enter:',
        try:
            confirm = raw_input('')
        except:
            confirm = "no"
            print
        if confirm != 'yes':
            error = 'Your keyring was not read or altered.'
            utils.print_error(error, title='Canceled')
        print
        for environment in env_list:
            username = '%s:%s' % (environment, parameter)
            try:
                delete_ok = self.multiclient.password_delete(username,
                                                             parameter)
            except:
                delete_ok = False
            if delete_ok:
                msg = '%s->%s' % (environment, parameter)
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (environment, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print
        utils.print_notice('If you encountered a failure deleting any of the'
                           ' credentials then you\nshould check your keyring'
                           ' configuration.', title='Complete')

    def set_password(self, parameter, env_list):
        utils.print_notice('Preparing to set a password in the keyring for:',
                           title='Keyring operation')
        print '  - Environments : %s' % '\n                    '.join(env_list)
        print '  - Parameter    : %s' % parameter
        print '\nIf this is correct, enter the corresponding credential ' \
              'to store in \nyour keyring or press CTRL-D to abort:',
        # Prompt for a password and catch a CTRL-D
        try:
            password = getpass.getpass('')
        except:
            password = None
            print
        print
        # Did we get a password from the prompt?
        if not password or len(password) < 1:
            utils.print_error('Your keyring was not read or altered.',
                              title='Canceled')
        for environment in env_list:
            # Try to store the password
            username = '%s:%s' % (environment, parameter)
            try:
                store_ok = self.multiclient.password_set(username, parameter,
                                                         password)
            except:
                store_ok = False
            if store_ok:
                msg = '%s->%s' % (environment, parameter)
                utils.print_notice(msg, title='Success')
            else:
                error = '%s->%s' % (environment, parameter)
                utils.print_error(error, title='Failed', exit=False)
        print
        utils.print_notice('If you encountered a failure storing any of the'
                           ' credentials then you\nshould check your keyring'
                           ' configuration.', title='Complete')

    def setup_base_args(self):
        """
        Sets up the base argparse object.
        """
        client_config = self.multiclient.get_all_config()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-l', '--list', action=utils._ListAction,
                                 dest='listenvs',
                                 client_config=client_config,
                                 help='list all configured environments')

    def run_keyring(self):
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

    def run_client(self):
        valid_envs = sorted(self.multiclient.get_environments())
        self.parser.add_argument('-x', '--executable', default=self.executable,
                                 help='command to run instead of '
                                      '%s' % self.executable)
        self.parser.add_argument('-d', '--debug', action='store_true',
                                 help='show client\'s debug output')
        self.parser.add_argument('env',
                                 help='environment to run the client against.',
                                 choices=valid_envs)
        multistack_args, client_args = self.parser.parse_known_args()
        if not client_args:
            error = 'No arguments were provided to pass along to the client.'
            utils.print_error(error, title='Missing client arguments')

        if multistack_args.env in self.multiclient.get_environments():
            self.set_client_env(multistack_args.env)
            self.multiclient.run_client(client_args, multistack_args)
        else:
            error = ('Environment \'%s\' not in multistack configuration '
                     'file' % multistack_args.env)
            utils.print_error(error, title='Missing environment')


def main_keyring():
    multistack_shell = MultiShell()
    multistack_shell.run_keyring()


def main_client():
    multistack_shell = MultiShell()
    multistack_shell.run_client()
