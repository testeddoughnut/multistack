#!/usr/bin/python
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


from setuptools import setup, find_packages


setup(
    name='multistack',
    version='0.1.0',
    author='M. David Bennett',
    author_email='mdavidbennett@syntheticworks.com',
    description='Universal wrapper for the various OpenStack client software '
                'with support for multiple environments.',
    install_requires=['keyring'],
    url='https://github.com/testeddoughnut/multistack',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'multiceilometer = multistack.ceilometer.shell:main_client',
            'multiceilometer-keyring = multistack.ceilometer.shell:main_keyring',
            'multicinder = multistack.cinder.shell:main_client',
            'multicinder-keyring = multistack.cinder.shell:main_keyring',
            'multiglance = multistack.glance.shell:main_client',
            'multiglance-keyring = multistack.glance.shell:main_keyring',
            'multiheat = multistack.heat.shell:main_client',
            'multiheat-keyring = multistack.heat.shell:main_keyring',
            'multikeystone = multistack.keystone.shell:main_client',
            'multikeystone-keyring = multistack.keystone.shell:main_keyring',
            'multineutron = multistack.neutron.shell:main_client',
            'multineutron-keyring = multistack.neutron.shell:main_keyring',
            'multinova = multistack.nova.shell:main_client',
            'multinova-keyring = multistack.nova.shell:main_keyring',
            'multiopenstack = multistack.openstack.shell:main_client',
            'multiopenstack-keyring = multistack.openstack.shell:main_keyring',
            'multiswift = multistack.swift.shell:main_client',
            'multiswift-keyring = multistack.swift.shell:main_keyring',
            'multitrove = multistack.trove.shell:main_client',
            'multitrove-keyring = multistack.trove.shell:main_keyring'],
        },
    )
