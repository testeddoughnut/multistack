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


import os
import setuptools

def read_file(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()

setuptools.setup(
    name='multistack',
    version='0.4.1',
    author='M. David Bennett',
    author_email='mdavidbennett@syntheticworks.com',
    description='Universal wrapper for the various OpenStack client software '
                'with support for multiple environments.',
    long_description=read_file("README.md"),
    license="Apache License, Version 2.0",
    install_requires=['keyring'],
    url='https://github.com/testeddoughnut/multistack',
    download_url = 'https://github.com/testeddoughnut/multistack/releases/latest',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: OpenStack",
        "Programming Language :: Python"
    ],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'test_*']),
    entry_points={
        'console_scripts': [
            'multistack-keyring = multistack.shell:main_keyring',
            'multiceilometer = multistack.clients.ceilometer:main_client',
            'multicinder = multistack.clients.cinder:main_client',
            'multiglance = multistack.clients.glance:main_client',
            'multiheat = multistack.clients.heat:main_client',
            'multikeystone = multistack.clients.keystone:main_client',
            'multineutron = multistack.clients.neutron:main_client',
            'multinova = multistack.clients.nova:main_client',
            'multiopenstack = multistack.clients.openstack:main_client',
            'multiswift = multistack.clients.swift:main_client',
            'multitrove = multistack.clients.trove:main_client',
            'multisolum = multistack.clients.solum:main_client'],
        },
    )
