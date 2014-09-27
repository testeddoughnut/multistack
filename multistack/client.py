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


import os
import re
import subprocess
import sys

from . import credentials

class MultiClient(object):

    def __init__(self, client_config):
        self.client_config = client_config
        self._client_env = None
        self.env_config = None
        self.env = os.environ.copy()
        self.prefix_list = ["os_"]

    @property
    def client_env(self):
        """
        Sets the client's environment to the provided entry.
        """
        return self._client_env

    @client_env.setter
    def client_env(self, new_env):
        """
        Sets the client's environment to the provided entry.
        """
        self.env_config = self.client_config.items(new_env)
        self._client_env = new_env

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
                credential = credentials.password_get(username, param)
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
        p.wait()
        # Return the return code of the process
        return p.returncode

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
