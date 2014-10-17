# MultiStack
### Easy authentication for multiple OpenStack environments
Made by M. David Bennett

### What is MultiStack?

MultiStack is a rewrite of [supernova](https://github.com/major/supernova) which was originally created by [Major Hayden](https://github.com/major). The goal of MultiStack is to provide the same convenience that supernova offers for all the various OpenStack clients. This is done by having a single base of code that can be reused for different clients by just changing a few variables. The different clients can authenticate using a common base of stored credentials through a flat-file or keyring.


### Migrating from supernova

Migrating to MultiStack from supernova is fairly easy in most cases. At the most basic level, all you need to do is rename your '.supernova' configuration file to '.multistack'. The only caveat is that some of the configuration items might need to be renamed to support all the clients. For example, a bunch of the original environment variables for nova client began with 'NOVA_'. These variables will still work when running 'multinova', however none of the other client wrappers will read these settings. Global configuration that should be passed to all of the clients should began with 'OS_', while specific configuration that should be read only for a specific client should began with the client's name (so 'NOVA_', for example). Grouping is handled differently in MultiStack than supernova, more information on that aspect later on. You will also need to setup any values you have stored in keyring for MultiStack since it uses a different entry in keyring than supernova.

### Installation

Installation is fairly simple via pip:

    pip install multistack

Or get the latest code from the github repo:

    git clone https://github.com/testeddoughnut/multistack.git
    cd multistack
    python setup.py install

You will also need to ensure that you have the clients that you're wanting MultiStack to wrap around installed. Novaclient, for example, can be installed through pip:

    pip install python-novaclient

### Configuration

The following locations are valid configuration files for MultiStack.

* ${XDG_CONFIG_HOME_}/multistack
* ~/.multistack
* ./.multistack

For MultiStack to work properly, each environment must be defined in the configuration file.  The data in the file is exactly the same as the environment variables which you would normally use when running the stand-alone client for your service. Global configuration that should be passed to all of the clients should began with 'OS_', while specific configuration that should be read only for a specific client should began with the client's name (so 'NOVA_', for example). The 'MULTISTACK_' prefix is used for configuration to be read by MultiStack. The available options are below:

Option                         | Description
-------------------------------|---------------------------------------------
MULTISTACK_GROUP               | Used to make an environment a group
MULTISTACK_$service_EXECUTABLE | Used to change the binary used for a service

Here's an example of how to use MultiStack with the [Rackspace Cloud](http://www.rackspace.com/cloud/servers/) in different datacenters:

    [dfw]
    OS_AUTH_URL = https://identity.api.rackspacecloud.com/v2.0/
    OS_REGION_NAME = DFW
    OS_USERNAME = your_rackspace_cloud_username
    OS_PASSWORD = your_rackspace_cloud_password(not API key)
    OS_TENANT_ID = your_rackspace_cloud_tenant_id
    OS_IMAGE_API_VERSION = 2
    TROVE_SERVICE_TYPE = "rax:database"

    [ord]
    OS_AUTH_URL = https://identity.api.rackspacecloud.com/v2.0/
    OS_REGION_NAME = ORD
    OS_USERNAME = your_rackspace_cloud_username
    OS_PASSWORD = your_rackspace_cloud_password(not API key)
    OS_TENANT_ID = your_rackspace_cloud_tenant_id
    OS_IMAGE_API_VERSION = 2
    TROVE_SERVICE_TYPE = "rax:database"

### Client Compatibility

Each client that MultiStack is compatible with has an executable that the setup.py script installs. MultiStack also installs an executable to work with the keyring called multistack-keyring. Below is a list of the clients that are currently supported. I have not tested all of them since I do not have a full blown OpenStack environment to play around with.

Client     | MultiStack client                        | Tested?
-----------|------------------------------------------|--------
ceilometer | multiceilometer                          | no
heat       | multiheat                                | yes
keystone   | multikeystone                            | yes
nova       | multinova                                | yes
trove      | multitrove                               | yes
cinder     | multicinder                              | no
glance     | multiglance                              | yes
neutron    | multineutron                             | no
openstack  | multiopenstack                           | no
swift      | multiswift                               | yes
solum      | multisolum                               | no

### Usage

The usage for the wrapper and the keyring app are below. For this example, I am using the novaclient wrapper, multinova:

    usage: multinova [-h] [-l] [-x EXECUTABLE] [-d]
                     {mine-dfw,mine-iad,mine-lon,mine-ord,mine-us}

    positional arguments:
      {dfw,iad,lon,ord,raxus}
                            environment to run the client against.

    optional arguments:
      -h, --help            show this help message and exit
      -l, --list            list all configured environments
      -x EXECUTABLE, --executable EXECUTABLE
                            command to run instead of nova
      -d, --debug           show client's debug output
      -r, --dryrun          Dry run. Output what would be ran but take no action.


    usage: multistack-keyring [-h] [-l] (-g | -s | -d) env [env ...] parameter

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

##### Specifying alternative executables

There are two ways to override the executable used when running MultiStack:

**1)** Passing '-x' or '--executable' to the client at runtime followed by the executable to be used, like so:

    multinova -x my_custom_nova_build ord list

**2)** Specifying it in the configuration section for a given environment in your MultiStack configuration. This works on a per-service basis, like so:

    [dfw]
    OS_AUTH_URL = https://identity.api.rackspacecloud.com/v2.0/
    OS_REGION_NAME = DFW
    MULTISTACK_SWIFT_EXECUTABLE = myswift

With this configuration present, using multiswift against the dfw environment will always use myswift as the executable. All other environments will not be affected.

##### Listing your configured environments

You can list all of your configured environments by using the `--list` argument on either the keyring app or the client wrapper.

### Working with keyrings
Due to security policies at certain companies or due to general paranoia, some users may not want API keys or passwords stored in a plaintext MultiStack configuration file.  Luckily, support is now available (via the [keyring](http://pypi.python.org/pypi/keyring) module) for storing any configuration value within your operating system's keychain.  This has been tested on the following platforms:

* Mac: Keychain Access.app
* Linux: gnome-keyring, kwallet (keyring will determine the backend to use based on the system type and configuration. Make sure if you're using linux without Gnome/KDE that you have pycrypto and simplejson/json installed so CryptedFileKeyring is supported or you end up with UncryptedFileKeyring and your keyring won't be encrypted)

To get started, you'll need to choose an environment and a configuration option.  Here's an example of some data you might not want to keep in plain text:

    multistack-keyring --set iad OS_PASSWORD

**TIP**: If you need to use the same data for multiple environments, you can use a global credential item very easily:

    multistack-keyring --set global MyCompanySSO

Alternatively, you may specify multiple environments:

    multistack-keyring --set iad ord OS_PASSWORD

Once it's stored, you can test a retrieval:

    # Normal, per-environment storage
    multistack-keyring --get production OS_PASSWORD

    # Global storage
    multistack-keyring --get global MyCompanySSO

You'll need to confirm that you want the data from your keychain displayed in plain text (to hopefully thwart shoulder surfers).

Once you've stored your sensitive data, simply adjust your MultiStack configuration file:

    #OS_PASSWORD = really_sensitive_api_key_here

    # If using storage per environment
    OS_PASSWORD = USE_KEYRING

    # If using global storage
    OS_PASSWORD = USE_KEYRING['MyCompanySSO']

When MultiStack reads your configuration file and spots a value of `USE_KEYRING`, it will look for credentials stored under `OS_PASSWORD` for that environment automatically.  If your keyring doesn't have a corresponding credential, you'll get an exception.

### Working with groups

MultiStack supports grouping environments into logical entities which allows you to run a command against multiple environments simultaneously. For example, I have my Rackspace regions grouped like so (some fields are omitted):

    [raxus]
    MULTISTACK_GROUP = dfw,ord,iad

    [dfw]
    OS_REGION_NAME = DFW
    TROVE_SERVICE_TYPE = "rax:database"

    [ord]
    OS_REGION_NAME = ORD
    TROVE_SERVICE_TYPE = "rax:database"

    [iad]
    OS_REGION_NAME = IAD
    TROVE_SERVICE_TYPE = "rax:database"

With this, I can issue commands to all three environments simultaneously like so:

    multitrove raxus list

At the moment MultiStack does not support nested groups (and may never will). An environment will be identified as a group by MultiStack if the option 'MULTISTACK_GROUP' exists in its section. If this option exists, all other options in that section are ignored.

### A brief note about environment variables

MultiStack will only replace and/or append environment variables to the already present variables for the duration of the client execution. If you have `OS_USERNAME` set outside the script, it won't be used in the script since the script will pull data from the configuration file to run the client. In addition, any variables which are set prior to running MultiStack will be left unaltered when the script exits.

### Adding support for additional clients

MultiStack is written to be easily extended to support additional clients as they come out. If you are interested in adding support for a new client, take a look at the files under the clients directory.
