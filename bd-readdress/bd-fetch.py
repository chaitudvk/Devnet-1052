#!/bin/python3
################################################################################
#                   ____  ____        _____    _       _                       #
#                  | __ )|  _ \      |  ___|__| |_ ___| |__                    #
#                  |  _ \| | | |_____| |_ / _ \ __/ __| '_ \                   #
#                  | |_) | |_| |_____|  _|  __/ || (__| | | |                  #
#                  |____/|____/      |_|  \___|\__\___|_| |_|                  #
#                                                                              #
#         == A simple tool to fetch Bridge Domain Gateway Parameters ==        #
#                                                                              #
################################################################################
#                                                                              #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, this software  #
#    is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF   #
#    ANY KIND, either express or implied.                                      #
#                                                                              #
################################################################################

# Standard Imports
import sys
import json

# External library imports:
from acitoolkit.acitoolkit import Session, Credentials
from acitoolkit.acitoolkit import Tenant, AppProfile, EPG, OutsideEPG
from acitoolkit.acitoolkit import Context, BridgeDomain, Subnet

from acitoolkit.acitoolkit import OutsideL3, OutsideEPG, Interface, L2Interface
from acitoolkit.acitoolkit import L3Interface, OSPFRouter, OSPFInterfacePolicy, OSPFInterface
from acitoolkit.acitoolkit import Contract

import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

# Internal imports
from tools import *

# FUNCTIONS
def print_banner():
    output("              ____  ____        _____    _       _                ")
    output("             | __ )|  _ \      |  ___|__| |_ ___| |__             ")
    output("             |  _ \| | | |_____| |_ / _ \ __/ __| '_ \            ")
    output("             | |_) | |_| |_____|  _|  __/ || (__| | | |           ")
    output("             |____/|____/      |_|  \___|\__\___|_| |_|           ")
    output("                                                                  ")
    output("                                                                  ")
    output("         == Bridge Domain GW Configuration Fetching Tool ==     \n")


# Start of the execution
if __name__ == "__main__":

    # Argument parsing. We use the ACI toolkit logic here, which tries to
    # retrieve credentials from the following places:
    # 1. Command line options
    # 2. Configuration file called credentials.py
    # 3. Environment variables
    # 4. Interactively querying the user
    # At the end, we should have an object args with all the necessary info.
    description = 'APIC credentials'
    creds = Credentials('apic', description)
    creds.add_argument('-o', "--output", default=None, help='Output file')
    creds.add_argument('-d', "--debug", default=None, help='Enable Debug mode')
    creds.add_argument('-f', "--filter", default=None, help='Retrieve only a single tenant')
    args = creds.get()
    
    # Let's check if the user passed all relevant parameters
    if args.output is None:
        fatal("[E] Output filename missing. Please pass it using --output <filename>")
    if args.debug is not None:
        debug_enable()

    # Welcome user with our cool banner ;-)
    print_banner()
    
    # Now, we log into the APIC
    session = Session(args.url, args.login, args.password)
    response = session.login()
    if response.ok is False:
        fatal(response.content)
    else:
        output("[+] Successfully connected to %s" % args.url)
    
    # Store fabric info here
    tenants_db = {}
    
    # Create output file
    f = open(args.output, "w")
    f.write("tenant-name,bd-name,bd-mac-addr,bd-flood-unicast,bd-flood-multicast,bd-flood-arp,bd-routing,bd-subnet-addr,bd-subnet-scope,bd-subnet-name\n")
    
    # Fetch existing Tenants and Bridge Domains
    tenants = Tenant.get(session)
    for t in tenants:
        
        # Filter out tenants if user passed --filter <tenant_name>
        if args.filter is not None:
            if t.name != args.filter:
                continue
        
        print("[+] Discovered Tenant '%s'" % t.name)
        tenants_db[t.name]={'object': t, 'bds':{}}
        bds = BridgeDomain.get(session, t)
        for b in bds:
            print(" |_ BD '%s'" % b.name)
            tenants_db[t.name]['bds'][b.name]={'object':b, 'subnets':{}}
            subnets = Subnet.get(session, b, t)
            for s in subnets:
                tenants_db[t.name]['bds'][b.name]['subnets'][s.get_addr()]=s
                print("   |_ Subnet '%s'" % s.get_addr())
                f.write("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" % 
                                          (t.name, b.name, b.get_mac(), 
                                           b.get_unknown_mac_unicast(),
                                           b.get_unknown_multicast(),
                                           b.get_arp_flood(),
                                           b.get_unicast_route(), 
                                           s.get_addr(),
                                           s.get_scope().replace(",", "|"),
                                           s.name))

    f.close()
    output("[+] Results written successfully to %s" % args.output)
    sys.exit(0)
