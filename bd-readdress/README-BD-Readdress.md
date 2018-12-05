        ____  ____        ____                _     _
       | __ )|  _ \      |  _ \ ___  __ _  __| | __| |_ __ ___  ___ ___
       |  _ \| | | |_____| |_) / _ \/ _` |/ _` |/ _` | '__/ _ \/ __/ __|
       | |_) | |_| |_____|  _ <  __/ (_| | (_| | (_| | | |  __/\__ \__ \
       |____/|____/      |_| \_\___|\__,_|\__,_|\__,_|_|  \___||___/___/

         == A simple tool to update Bridge Domain Subnet Addresses ==

Introduction
=============
BD-Readdress is a command-line tool to push Bridge Domain and L3 gateway 
configuration changes to a given fabric. As input, it takes the output file
produced by the BD-Fetch tool (a list of parameters for different L3 gateways
as comma-separated values). 

The tool reads the input file, gathers information about the current state of 
the target fabric, and makes the necessary changes to it to replicate the 
configuration on the input file.

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

    $ ./bd-readdress --input <filename.csv> 

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


By default, the tool will only display potential changes to be made to the 
target fabric but will not make any of them effective. In order to instruct
the tool to push the new configuration, the "--commit yes" parameters should be
passed from the command line. In addition, the tool will not remove any
L3 gateways/subnets that already exist on the BDs being configured. In order
to force removal of such existing subnets, "--remove yes" should be passed
from the command-line.

Finally, the --help parameter will display a list of all available options.

    $ ./bd-readdress.py --help
    usage: bd-readdress.py [-h] [-u URL] [-l LOGIN] [-p PASSWORD]
                           [-i INPUT] [-c COMMIT] [-r REMOVE] [-d DEBUG]
    
    APIC credentials
    
    optional arguments:
      -h, --help            show this help message and exit
      -u URL, --url URL     APIC IP address.
      -l LOGIN, --login LOGIN
                            APIC login ID.
      -p PASSWORD, --password PASSWORD
                            APIC login password.
      -i INPUT, --input INPUT
                            Input file
      -c COMMIT, --commit COMMIT
                            Make changes effective
      -r REMOVE, --remove REMOVE
                            Remove existing BD subnets
      -d DEBUG, --debug DEBUG
                            Enable Debug mode
    
    


Usage Examples
==============

Here are some usage examples (including the generation of the input file 
using bd-fetch)
    
    $ ./bd-fetch.py --output "fabric-feltham.csv" --filter "NProd-Dev"
                  ____  ____        _____    _       _
                 | __ )|  _ \      |  ___|__| |_ ___| |__
                 |  _ \| | | |_____| |_ / _ \ __/ __| '_ \
                 | |_) | |_| |_____|  _|  __/ || (__| | | |
                 |____/|____/      |_|  \___|\__\___|_| |_|
    
    
             == Bridge Domain GW Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.255.100.110
    [+] Discovered Tenant 'NProd-Dev'
     |_ BD 'BD-001'
       |_ Subnet '1.0.0.1/24'
     |_ BD 'BD-002'
       |_ Subnet '2.0.0.1/24'
     |_ BD 'BD-003'
       |_ Subnet '3.0.0.1/24'
    [+] Results written successfully to fabric-feltham.csv


    $ ./bd-readdress.py --input fabric-feltham.csv -u https://10.255.103.110
      ____  ____        ____                _     _
     | __ )|  _ \      |  _ \ ___  __ _  __| | __| |_ __ ___  ___ ___
     |  _ \| | | |_____| |_) / _ \/ _` |/ _` |/ _` | '__/ _ \/ __/ __|
     | |_) | |_| |_____|  _ <  __/ (_| | (_| | (_| | | |  __/\__ \__ \
     |____/|____/      |_| \_\___|\__,_|\__,_|\__,_|_|  \___||___/___/
    
               == Bridge Domain Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.255.103.110
    [+] Objects discovered on the current fabric 'https://10.255.103.110'
     |_ Tenant 'NProd-Dev'
     |  |_ BD 'BD-001'
     |  |  |_ GW '1.0.0.2/24'
     |  |_ BD 'BD-002'
     |  |  |_ GW '2.0.0.2/24'
     |  |_ BD 'BD-003'
     |  |  |_ GW '3.0.0.2/24'
    [+] Changes to be applied to the current fabric 'https://10.255.103.110'
     |_ Subnet NProd-Dev/BD-001/1.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Subnet NProd-Dev/BD-002/2.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Subnet NProd-Dev/BD-003/3.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Existing Subnet NProd-Dev/BD-002/2.0.0.2/24 will be kept intact because no '--remove yes' was supplied.
     |_ Existing Subnet NProd-Dev/BD-003/3.0.0.2/24 will be kept intact because no '--remove yes' was supplied.
     |_ Existing Subnet NProd-Dev/BD-001/1.0.0.2/24 will be kept intact because no '--remove yes' was supplied.
    [+] No configuration pushed because '--commit yes' not supplied.



    $ ./bd-readdress.py --input fabric-feltham.csv -u https://10.255.103.110 --commit yes --remove yes
      ____  ____        ____                _     _
     | __ )|  _ \      |  _ \ ___  __ _  __| | __| |_ __ ___  ___ ___
     |  _ \| | | |_____| |_) / _ \/ _` |/ _` |/ _` | '__/ _ \/ __/ __|
     | |_) | |_| |_____|  _ <  __/ (_| | (_| | (_| | | |  __/\__ \__ \
     |____/|____/      |_| \_\___|\__,_|\__,_|\__,_|_|  \___||___/___/
    
               == Bridge Domain Configuration Fetching Tool ==
    
    [+] Successfully connected to https://10.255.103.110
    [+] Objects discovered on the current fabric 'https://10.255.103.110'
     |_ Tenant 'NProd-Dev'
     |  |_ BD 'BD-001'
     |  |  |_ GW '1.0.0.2/24'
     |  |_ BD 'BD-002'
     |  |  |_ GW '2.0.0.2/24'
     |  |_ BD 'BD-003'
     |  |  |_ GW '3.0.0.2/24'
    [+] Changes to be applied to the current fabric 'https://10.255.103.110'
     |_ Subnet NProd-Dev/BD-001/1.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Subnet NProd-Dev/BD-002/2.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Subnet NProd-Dev/BD-003/3.0.0.1/24 did not exist and will be added.
       |_ MAC Address will be updated to '00:22:BD:F8:19:FF'
     |_ Existing Subnet NProd-Dev/BD-003/3.0.0.2/24 will be REMOVED from the fabric.
     |_ Existing Subnet NProd-Dev/BD-001/1.0.0.2/24 will be REMOVED from the fabric.
     |_ Existing Subnet NProd-Dev/BD-002/2.0.0.2/24 will be REMOVED from the fabric.
    [+] Pushing configuration for Tenant 'NProd-Dev'
    [+] Configuration for Tenant 'NProd-Dev' pushed successfully


License
=======
Copyright (c) 2015 Cisco Systems. All Rights Reserved.

Unless required by applicable law or agreed to in writing, this software
is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
ANY KIND, either express or implied. This software is explicitly excluded
from Cisco TAC support, Cisco Advanced Services support and any other kind
of support from Cisco.

