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


import ConfigParser
import keyring
import os
import re
import subprocess
import sys


class MultiClient(object):

    def __init__(self):
        self.client_config = None
        self.client_env = None
        self.env_config = None
        self.env = os.environ.copy()
        self.prefix_list = ["os_"]

    def read_config(self):
        """
        Reads the multistack config file from the current directory or the
        user's home directory.
        """
        possible_configs = [os.path.expanduser("~/.multistack"), '.multistack']
        self.client_config = ConfigParser.RawConfigParser()
        self.client_config.read(possible_configs)

    def _set_env_config(self, new_env):
        """
        Sets the set the config for the currently selected environment.
        """
        if not self.client_config:
            self.read_config()
        new_env_config = self.client_config.items(new_env)
        self.env_config = new_env_config

    def get_all_config(self):
        if not self.client_config:
            self.read_config()
        environments = {}
        for environment in self.client_config.sections():
            environments[environment] = self.client_config.items(environment)
        return environments

    def set_client_env(self, new_env):
        """
        Sets the client's environment to the provided entry.
        """
        self._set_env_config(new_env)
        self.client_env = new_env

    def get_environments(self):
        """
        Checks to see if the configuration file contains a section for our
        requested environment.
        """
        if not self.client_config:
            self.read_config()
        return self.client_config.sections()

    def password_get(self, username, parameter):
        """
        Retrieves a password from the keychain based on the environment and
        configuration parameter pair.
        """
        try:
            return keyring.get_password('multistack', username).encode('ascii')
        except:
            return False

    def password_set(self, username, parameter, password):
        """
        Stores a password in a keychain for a particular environment and
        configuration parameter pair.
        """
        try:
            keyring.set_password('multistack', username, password)
            return True
        except:
            return False

    def password_delete(self, username, parameter):
        """
        Deletes a password from the keychain for a particular environment and
        configuration parameter pair.
        """
        try:
            keyring.delete_password('multistack', username)
            return True
        except:
            return False

    def prep_creds(self):
        """
        Finds relevant config options in the multistack config and cleans them
        up for the client.
        """
        client_re = re.compile(r"(^%s)" % "|^".join(self.prefix_list))

        creds = []
        for param, value in self.env_config:

            # Skip parameters we're unfamiliar with
            if not client_re.match(param):
                continue

            param = param.upper()

            # Get values from the keyring if we find a USE_KEYRING constant
            if value.startswith("USE_KEYRING"):
                rex = "USE_KEYRING\[([\x27\x22])(.*)\\1\]"
                if value == "USE_KEYRING":
                    username = "%s:%s" % (self.client_env, param)
                else:
                    global_identifier = re.match(rex, value).group(2)
                    username = "%s:%s" % ('global', global_identifier)
                credential = self.password_get(username, param)
            else:
                credential = value.strip("\"'")

            # Make sure we got something valid from the configuration file or
            # the keyring
            if not credential:
                msg = "Attempted to retrieve a credential for %s but " \
                      "couldn't find it within the keyring." % username
                raise Exception(msg)

            creds.append((param, credential))

        return creds

    def prep_shell_environment(self):
        """
        Appends new variables to the current shell environment temporarily.
        """
        for k, v in self.prep_creds():
            self.env[k] = v

    def run_client(self, client_args, multistack_args):
        """
        Sets the environment variables for the client, runs the client, and
        prints the output.
        """
        # Get the environment variables ready
        self.prep_shell_environment()

        # Check for a debug override
        if multistack_args.debug:
            client_args.insert(0, '--debug')

        p = subprocess.Popen([multistack_args.executable] + client_args,
                             stdout=sys.stdout, stderr=sys.stderr,
                             env=self.env)
        # Don't exit until we're sure the subprocess has exited
        return p.wait()

    def get_client(self, env):
        """
        Returns python client object authenticated with multistack config.
        """
        raise NotImplementedError()

    def prep_python_creds(self):
        """
        Prepare credentials for python client instantiation.
        """
        raise NotImplementedError()
