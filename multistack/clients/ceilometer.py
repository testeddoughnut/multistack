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


from multistack import client
from multistack import shell


class MultiCeilometer(client.MultiClient):

    def __init__(self, client_config):
        super(MultiCeilometer, self).__init__(client_config)
        self.prefix_list += ["ceilometer_", "ceilometerclient_"]


def main_client():
    multistack_shell = shell.MultiShell('ceilometer', MultiCeilometer)
    multistack_shell.run_client()
