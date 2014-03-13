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


from novaclient import client as novaclient
from novaclient import auth_plugin
from multistack import client


class MultiNova(client.MultiClient):

    def __init__(self):
        super(MultiNova, self).__init__()
        self.prefix_list += ["nova_", "novaclient_"]

    def get_client(self, version):
        """
        Returns python client object authenticated with multistack config.
        """
        username, api_key, project_id, kwargs = self.prep_python_creds()
        return novaclient.Client(version, username, api_key, project_id,
                                 **kwargs)

    def prep_python_creds(self):
        """
        Prepare credentials for python Client instantiation.
        """
        def rm_prefix(name):
            for prefix in self.prefix_list:
                if name.startswith(prefix):
                    return name[len(prefix):]
            else:
                return name

        creds = dict((rm_prefix(k[0].lower()), k[1])
                     for k in self.prep_creds())
        if creds.get('auth_system'):
            auth_plugin.discover_auth_systems()
            nova_auth_plugin = auth_plugin.load_plugin(creds['auth_system'])
            creds['auth_plugin'] = nova_auth_plugin
        if creds.get('url'):
            creds['auth_url'] = creds.pop('url')
        username = creds.pop('username', None)
        if creds.get('tenant_name') and not creds.get('project_id'):
            creds['project_id'] = creds.pop('tenant_name')
        else:
            creds.pop('tenant_name', None)
        project_id = creds.pop('project_id', None)
        if creds.get('password'):
            api_key = creds.pop('password')
        else:
            api_key = creds.pop('api_key', None)
        return username, api_key, project_id, creds
