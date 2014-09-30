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
"""
Takes care of the basic setup of the config files
"""
try:
    import ConfigParser
except:
    import configparser as ConfigParser

import os


def load_multistack_config():
    """
    Pulls the multistack configuration file and reads it
    """
    xdg_config_home = os.environ.get('XDG_CONFIG_HOME') or \
        os.path.expanduser('~/.config')
    possible_configs = [os.path.join(xdg_config_home, "multistack"),
                        os.path.expanduser("~/.multistack"),
                        ".multistack"]
    multistack_config = ConfigParser.RawConfigParser()
    multistack_config.read(possible_configs)
    return multistack_config


def is_env_group(client_config, env):
    return client_config.has_option(env, 'MULTISTACK_GROUP')


def get_group_members(client_config, env):
    return client_config.get(env, 'MULTISTACK_GROUP').split(',')
