                   ____  ____        _____    _       _ 
                  | __ )|  _ \      |  ___|__| |_ ___| |__
                  |  _ \| | | |_____| |_ / _ \ __/ __| '_ \
                  | |_) | |_| |_____|  _|  __/ || (__| | | |
                  |____/|____/      |_|  \___|\__\___|_| |_|

         == A simple tool to fetch Bridge Domain Gateway Parameters ==

Introduction
=============
BD-Fetch is a simple command-line tool to retrieve Bridge Domain and L3 gateway
information from a given fabric, and store it on an external CSV file. Such file
can later be used as an input to the BD-Readdress tool to push the same BD
configuration to a different fabric, or to restore state on the same original
fabric after changes have been made.

Note that this tool operates only at the Bridge Domain and L3 subnet level.

Requirements
=============
* Python Python3.4 or above.
* Python's "requests" library
  * https://github.com/kennethreitz/requests/zipball/master
* The ACI toolkit, JS-release branch
  * https://github.com/luismartingarcia/acitoolkit/archive/js-release.zip

Usage
=====

    $ ./bd-fetch --output <filename.csv> 

The application assumes that APIC address, username and password, are
stored on a file named *credentials.py* located in the same directory. The 
content of the *credentials.py* file must follow this format:

    URL="https://192.168.0.90"
    LOGIN="admin"
    PASSWORD="Ap1cPass123"

Credentials may also me passed directly from the command-line using
parameters -u <APIC_URL> -l <USERNAME> -p <PASSWORD>

If *credentials.py* does not exist and no credentials are supplied from
the command line, the application will ask for them interactively. 

The tool also offers the posibility to limit the information retrieved from
the fabric to a single tenant using the --tenant <TENANT_NAME> parameter.

Finally, the --help parameter will display a list of all available options.

    $ ./bd-fetch.py --help
    usage: bd-fetch.py [-h] [-u URL] [-l LOGIN] [-p PASSWORD]
                       [-o OUTPUT] [-d DEBUG] [-f FILTER]
    
    APIC credentials
    
    optional arguments:
      -h, --help            show this help message and exit
      -u URL, --url URL     APIC IP address.
      -l LOGIN, --login LOGIN
                            APIC login ID.
      -p PASSWORD, --password PASSWORD
                            APIC login password.
      -o OUTPUT, --output OUTPUT
                            Output file
      -d DEBUG, --debug DEBUG
                            Enable Debug mode
      -f FILTER, --filter FILTER
                            Retrieve only a single tenant



Usage Examples
==============

    $ ./bd-fetch.py --output "fabric-A.csv"
                  ____  ____        _____    _       _
                 | __ )|  _ \      |  ___|__| |_ ___| |__
                 |  _ \| | | |_____| |_ / _ \ __/ __| '_ \
                 | |_) | |_| |_____|  _|  __/ || (__| | | |
                 |____/|____/      |_|  \___|\__\___|_| |_|
    
    
             == Bridge Domain GW Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.48.59.239
    [+] Discovered Tenant 'common'
     |_ BD 'bd2_e717df4f-bb05-4b73-b940-82ab4f66294e'
     |_ BD 'default'
     |_ BD 'VLAN-46-BD'
    [+] Discovered Tenant 'SDK_Demo'
     |_ BD 'Main-BD'
       |_ Subnet '192.168.66.1/24'
       |_ Subnet '192.168.67.1/24'
    [+] Results written successfully to fabric-A.csv



    
    $ ./bd-fetch.py --output "fabric-A.csv" --filter SDK_Demo
                  ____  ____        _____    _       _
                 | __ )|  _ \      |  ___|__| |_ ___| |__
                 |  _ \| | | |_____| |_ / _ \ __/ __| '_ \
                 | |_) | |_| |_____|  _|  __/ || (__| | | |
                 |____/|____/      |_|  \___|\__\___|_| |_|
    
    
             == Bridge Domain GW Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.48.59.239
    [+] Discovered Tenant 'SDK_Demo'
     |_ BD 'Main-BD'
       |_ Subnet '192.168.66.1/24'
       |_ Subnet '192.168.67.1/24'
    [+] Results written successfully to fabric-A.csv



    
    $ ./bd-fetch.py --output "fabric-B.csv" -u "https://10.48.59.234" -l "admin" -p "cisco123"
                  ____  ____        _____    _       _
                 | __ )|  _ \      |  ___|__| |_ ___| |__
                 |  _ \| | | |_____| |_ / _ \ __/ __| '_ \
                 | |_) | |_| |_____|  _|  __/ || (__| | | |
                 |____/|____/      |_|  \___|\__\___|_| |_|
    
    
             == Bridge Domain GW Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.48.59.234
    [+] Discovered Tenant 'common'
     |_ BD 'default'
    [+] Discovered Tenant 'infra'
     |_ BD 'default'
       |_ Subnet '10.0.0.30/27'
    [+] Discovered Tenant 'POD6'
     |_ BD 'POD6_BD1'
       |_ Subnet '1.1.1.1/30'
    [+] Discovered Tenant 'mgmt'
     |_ BD 'inb'
       |_ Subnet '1.2.12.1/24'
    [+] Results written successfully to fabric-B.csv


License
=======
Copyright (c) 2015 Cisco Systems. All Rights Reserved.

Unless required by applicable law or agreed to in writing, this software
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied. This software is explicitly excluded
from Cisco TAC support, Cisco Advanced Services support and any other kind
of support from Cisco.

