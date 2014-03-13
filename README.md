# MultiStack
### Easy authentication for multiple OpenStack environments
Made by M. David Bennett

### What is MultiStack?

MultiStack is a rewrite of [supernova](https://github.com/major/supernova) which was originally created by [Major Hayden](https://github.com/major). The goal of MultiStack is to provide the same convenience that supernova offers for all the various OpenStack clients. This is done by having a single base of code that can be reused for different clients by just changing a few variables. The different clients can authenticate using a common base of stored credentials through a flat-file or keyring.


### Migrating from supernova

Migrating to MultiStack from supernova is fairly easy in most cases. At the most basic level, all you need to do is rename your '.supernova' configuration file to '.multistack'. The only caveat is that some of the configuration items might need to be renamed to support all the clients. For example, a bunch of the original environment variables for nova client began with 'NOVA_'. These variables will still work when running 'multinova', however none of the other client wrappers will read these settings. Global configuration that should be passed to all of the clients should began with 'OS_', while specific configuration that should be read only for a specific client should began with the client's name (so 'NOVA_', for example). You will also need to setup any values you have stored in keyring for MultiStack since it uses a different entry in keyring than supernova.

### Installation

Installation is fairly simple:

    git clone https://github.com/testeddoughnut/multistack.git
    cd multistack
    python setup.py install

You will also need to ensure that you have the clients that you're wanting MultiStack to wrap around installed. Novaclient, for example, can be installed through pip:

    pip install python-novaclient

### Configuration

For MultiStack to work properly, each environment must be defined in `~/.multistack` (a file in your user's home directory).  The data in the file is exactly the same as the environment variables which you would normally use when running the stand-alone client for your service. Global configuration that should be passed to all of the clients should began with 'OS_', while specific configuration that should be read only for a specific client should began with the client's name (so 'NOVA_', for example).

Here's an example of how to use MultiStack with the [Rackspace Cloud](http://www.rackspace.com/cloud/servers/) in different datacenters (credit for this goes [here](http://blog.chmouel.com/2013/09/27/how-to-access-rackspace-cloud-with-latest-swiftclient-novaclient/)):

    [iad]
    OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/
    OS_REGION_NAME=IAD
    OS_TENANT_NAME=" "
    OS_USERNAME=your_rackspace_cloud_username
    OS_PASSWORD=your_rackspace_cloud_password(not API key)

    [ord]
    OS_AUTH_URL=https://identity.api.rackspacecloud.com/v2.0/
    OS_REGION_NAME=ORD
    OS_TENANT_NAME=" "
    OS_USERNAME=your_rackspace_cloud_username
    OS_PASSWORD=your_rackspace_cloud_password(not API key)

### Client Compatibility

Each client that MultiStack is compatible with has two executables that the setup.py script installs, one for running the client and one for modifying the keyring settings. In all actuality, the keyring executable is pretty much identical for all the different clients and a change made with one will be reflected for all of them. Below is a list of the clients that are currently supported. I have not tested all of them since I do not have a full blown OpenStack environment to play around with.

Client     | MultiStack client and keyring app        | Tested?
-----------|------------------------------------------|--------
ceilometer | multiceilometer, multiceilometer-keyring | no
heat       | multiheat, multiheat-keyring             | no
keystone   | multikeystone, multikeystone-keyring     | yes
nova       | multinova, multinova-keyring             | yes
trove      | multitrove, multitrove-keyring           | no
cinder     | multicinder, multicinder-keyring         | no
glance     | multiglance, multiglance-keyring         | yes
neutron    | multineutron, multineutron-keyring       | no
openstack  | multiopenstack, multiopenstack-keyring   | no
swift      | multiswift, multiswift-keyring           | yes

### Usage

The usage for the wrapper and the keyring app are below. For this example, I am using the novaclient wrapper, multinova:

    usage: multinova [-h] [-l] [-x EXECUTABLE] [-d] {}

    positional arguments:
      {}                    environment to run the client against.

    optional arguments:
      -h, --help            show this help message and exit
      -l, --list            list all configured environments
      -x EXECUTABLE, --executable EXECUTABLE
                            command to run instead of nova
      -d, --debug           show client's debug output


    usage: multinova-keyring [-h] [-l] (-g | -s | -d) env [env ...] parameter

    positional arguments:
      env           environment to set parameter in
      parameter     parameter to set

    optional arguments:
      -h, --help    show this help message and exit
      -l, --list    list all configured environments
      -g, --get     retrieves credentials from keychain storage
      -s, --set     stores credentials in keychain storage
      -d, --delete  deletes credentials in keychain storage

##### Passing commands to the client

For example, if you wanted to list all instances within the **iad** environment using multinova:

    multinova iad list

List all the containers for swift in ORD:

    multiswift ord list

The first argument is generally the environment argument and it is expected to be a single word without spaces. Any text after the environment argument is passed directly to the client.

##### Debug override

You may optionally pass `--debug` as the first argument (before the environment argument) to see additional debug information about the requests being made to the API:

    multinova --debug iad list

As before, any text after the environment argument is passed directly to the client.

##### Listing your configured environments

You can list all of your configured environments by using the `--list` argument on either the keyring app or the client wrapper.

### Working with keyrings
Due to security policies at certain companies or due to general paranoia, some users may not want API keys or passwords stored in a plaintext MultiStack configuration file.  Luckily, support is now available (via the [keyring](http://pypi.python.org/pypi/keyring) module) for storing any configuration value within your operating system's keychain.  This has been tested on the following platforms:

* Mac: Keychain Access.app
* Linux: gnome-keyring, kwallet (keyring will determine the backend to use based on the system type and configuration. Make sure if you're using linux without Gnome/KDE that you have pycrypto and simplejson/json installed so CryptedFileKeyring is supported or you end up with UncryptedFileKeyring and your keyring won't be encrypted)

To get started, you'll need to choose an environment and a configuration option.  Here's an example of some data you might not want to keep in plain text:

    multinova-keyring --set iad OS_PASSWORD

**TIP**: If you need to use the same data for multiple environments, you can use a global credential item very easily:

    multinova-keyring --set global MyCompanySSO

Alternatively, you may specify multiple environments:

    multinova-keyring --set iad ord OS_PASSWORD

Once it's stored, you can test a retrieval:

    # Normal, per-environment storage
    multinova-keyring --get production OS_PASSWORD

    # Global storage
    multinova-keyring --get global MyCompanySSO

You'll need to confirm that you want the data from your keychain displayed in plain text (to hopefully thwart shoulder surfers).

Once you've stored your sensitive data, simply adjust your MultiStack configuration file:

    #OS_PASSWORD = really_sensitive_api_key_here

    # If using storage per environment
    OS_PASSWORD = USE_KEYRING

    # If using global storage
    OS_PASSWORD = USE_KEYRING['MyCompanySSO']

When MultiStack reads your configuration file and spots a value of `USE_KEYRING`, it will look for credentials stored under `OS_PASSWORD` for that environment automatically.  If your keyring doesn't have a corresponding credential, you'll get an exception.

#### A brief note about environment variables

MultiStack will only replace and/or append environment variables to the already present variables for the duration of the client execution. If you have `OS_USERNAME` set outside the script, it won't be used in the script since the script will pull data from `~/.multistack` and use it to run the client. In addition, any variables which are set prior to running MultiStack will be left unaltered when the script exits.

### Adding support for additional clients

MultiStack is written to be easily extended to support additional clients as they come out. If you are interested in adding support for a new client, take a look at the files under one of the client directories (like `nova` for example).