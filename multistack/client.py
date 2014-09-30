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

import os
import re
import subprocess
import sys
from . import config
from . import credentials
from . import utils


class MultiClient(object):

    def __init__(self):
        self.client_config = config.load_multistack_config()
        self.available_envs = sorted(self.client_config.sections())
        self._client_env = None
        self.run_config = []
        self.default_executable = None
        self.prefix_list = ['os_', 'multistack_']

    @property
    def client_env(self):
        """
        Returns the client's current environment.
        """
        return self._client_env

    @client_env.setter
    def client_env(self, new_env):
        """
        Sets the client's environment to the provided entry.
        """
        new_run_config = []
        if new_env not in self.available_envs:
            msg = ('Environment \'%s\' is not in the multistack configuration '
                   'file' % new_env)
            raise AttributeError(msg)
        if config.is_env_group(self.client_config, new_env):
            group_members = config.get_group_members(self.client_config,
                                                     new_env)
            # Check that the members actually exist and that they aren't groups
            # themselves.
            for member in group_members:
                if member not in self.available_envs:
                    msg = ('Group member \'%s\' is not in the multistack '
                           'configuration file' % member)
                    raise AttributeError(msg)
                if config.is_env_group(self.client_config, member):
                    msg = ('Group member \'%s\' is itself a group. Nested '
                           'groups are unsupported at this time.' % member)
                    raise AttributeError(msg)
                env_config = self.get_env_config(member)
                executable = self.get_executable(env_config)
                new_run_config.append([member, executable, env_config])
        else:
            env_config = self.get_env_config(new_env)
            executable = self.get_executable(env_config)
            new_run_config.append([new_env, executable, env_config])
        self.run_config = new_run_config
        self._client_env = new_env

    def prep_creds(self, env):
        """
        Finds relevant config options in the multistack config and cleans them
        up for the client.
        """
        client_re = re.compile(r"(^%s)" % "|^".join(self.prefix_list))

        creds = []
        for param, value in self.client_config.items(env):

            # Skip parameters we're unfamiliar with
            if not client_re.match(param):
                continue

            param = param.upper()

            # Get values from the keyring if we find a USE_KEYRING constant
            if value.startswith("USE_KEYRING"):
                rex = "USE_KEYRING\[([\x27\x22])(.*)\\1\]"
                if value == "USE_KEYRING":
                    credential = credentials.password_get(env, param)
                else:
                    global_id = re.match(rex, value).group(2)
                    credential = credentials.password_get('global', global_id)
            else:
                credential = value.strip("\"'")

            # Make sure we got something valid from the configuration file or
            # the keyring
            if not credential:
                msg = ("Attempted to retrieve a credential for \'%s\'->\'%s\' "
                       "but couldn't find it within the keyring." % (env,
                                                                     param))
                raise AttributeError(msg)

            creds.append((param, credential))

        return creds

    def get_env_config(self, env):
        """
        Appends new variables to the current shell environment temporarily.
        """
        env_config = os.environ.copy()
        # env_config = {}
        for k, v in self.prep_creds(env):
            env_config[k] = v
        return env_config

    def get_executable(self, env_config):
        if env_config.get('MULTISTACK_%s_EXECUTABLE' %
                          self.default_executable.upper()):
            executable = env_config['MULTISTACK_%s_EXECUTABLE' %
                                    self.default_executable.upper()]
        else:
            executable = self.default_executable
        return executable

    def run_client(self, client_args, multistack_args):
        """
        Sets the environment variables for the client, runs the client, and
        prints the output.
        """
        # Check for a debug override
        if multistack_args.debug:
            client_args.insert(0, '--debug')
        for env, executable, env_config in self.run_config:
            # set the executable
            if multistack_args.executable:
                run_executable = multistack_args.executable
            else:
                run_executable = executable
            utils.print_notice("Running %s against %s..." % (
                               run_executable, env))
            process = subprocess.Popen([run_executable] + client_args,
                                       stdout=sys.stdout, stderr=sys.stderr,
                                       env=env_config)
            # Don't exit until we're sure the subprocess has exited
            process.wait()
            # Return the return code of the process
        return process.returncode

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
