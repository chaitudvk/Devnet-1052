#!/bin/python3
################################################################################
#        ____  ____        ____                _     _                         #
#       | __ )|  _ \      |  _ \ ___  __ _  __| | __| |_ __ ___  ___ ___       #
#       |  _ \| | | |_____| |_) / _ \/ _` |/ _` |/ _` | '__/ _ \/ __/ __|      #
#       | |_) | |_| |_____|  _ <  __/ (_| | (_| | (_| | | |  __/\__ \__ \      #
#       |____/|____/      |_| \_\___|\__,_|\__,_|\__,_|_|  \___||___/___/      #
#                                                                              #
#         == A simple tool to update Bridge Domain Subnet Addresses ==         #
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
import csv

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
    output("  ____  ____        ____                _     _                   ")
    output(" | __ )|  _ \      |  _ \ ___  __ _  __| | __| |_ __ ___  ___ ___ ")
    output(" |  _ \| | | |_____| |_) / _ \/ _` |/ _` |/ _` | '__/ _ \/ __/ __|")
    output(" | |_) | |_| |_____|  _ <  __/ (_| | (_| | (_| | | |  __/\__ \__ \\")
    output(" |____/|____/      |_| \_\___|\__,_|\__,_|\__,_|_|  \___||___/___/")
    output("                                                                  ")
    output("           == Bridge Domain Configuration Fetching Tool ==      \n")


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
    creds.add_argument('-i', "--input", default=None, help='Input file')
    creds.add_argument('-c', "--commit", default=None, help='Make changes effective')
    creds.add_argument('-r', "--remove", default=None, help='Remove existing BD subnets')
    creds.add_argument('-d', "--debug", default=None, help='Enable Debug mode')
    args = creds.get()
    
    # Let's check if the user passed all relevant parameters:
    # 1. Input file (mandatory)
    if args.input is None:
        fatal("[E] Input filename missing. Please pass it using --output <filename>")
    # 2. Enable debug output (default: No)
    if args.debug is not None:
        debug_enable()
    # 3. Remove existing BD gayeways (default: No)
    if args.remove is not None and args.remove.lower() in ["y", "yes", "true"]:
        args.remove=True
    else:
        args.remove=False
    # 4. Make changes persistent on the target APIC (default: No)
    if args.commit is not None and args.commit.lower() in ["y", "yes", "true"]:
        args.commit=True
    else:
        args.commit=False

    # Welcome user with our cool banner ;-)
    print_banner()
    
    # Now, we log into the APIC
    session = Session(args.url, args.login, args.password)
    response = session.login()
    if response.ok is False:
        fatal(response.content)
    else:
        output("[+] Successfully connected to %s" % args.url)
    
    # First of all, let's retrieve a bunch of data from the fabric we connected to
    existing_tenants = {}
    tenants_modified = {}
    tenants = Tenant.get(session)
    print("[+] Objects discovered on the current fabric '%s'" % args.url)
    for t in tenants:
        print(" |_ Tenant '%s'" % t.name)
        existing_tenants[t.name]={'object': t, 'bds':{}}
        bds = BridgeDomain.get(session, t)
        for b in bds:
            print(" |  |_ BD '%s'" % b.name)
            existing_tenants[t.name]['bds'][b.name]={'object':b, 'subnets':{}}
            subnets = Subnet.get(session, b, t)
            for s in subnets:
                existing_tenants[t.name]['bds'][b.name]['subnets'][s.get_addr()]=s
                print(" |  |  |_ GW '%s'" % s.get_addr())
               
    # Now, let's read the input file and for each GW, update the config on 
    # the fabric
    f = open(args.input, "r")
    input_tenants={}
    print("[+] Changes to be applied to the current fabric '%s'" % args.url)
    for gw_info in csv.DictReader(f):

        # Store info in simpler variables
        tn = gw_info['tenant-name']
        bd = gw_info['bd-name']
        sn = gw_info['bd-subnet-addr']
        scope = gw_info['bd-subnet-scope'].replace("|", ",")
        flood_uni = gw_info['bd-flood-unicast']
        flood_multi = gw_info['bd-flood-multicast']
        flood_arp = gw_info['bd-flood-arp']
        do_routing = gw_info['bd-routing']
        mac_addr = gw_info['bd-mac-addr']
        
        # Store it also in a dict so we can index it and retrieve it easily later
        if tn not in input_tenants:
            input_tenants[tn]={'bds':{}}
        if bd not in input_tenants[tn]['bds']:
            input_tenants[tn]['bds'][bd]={'subnets':{}}
        if sn not in input_tenants[tn]['bds'][bd]['subnets']:
            input_tenants[tn]['bds'][bd]['subnets'][sn]=sn

        # Fetch BD object
        try:
            bd_obj      = existing_tenants[tn]['bds'][bd]['object']
            bd_subnets  = existing_tenants[tn]['bds'][bd]['subnets']
        # We do nothing for BDs that don't exist on the target fabric
        except:
            warning(" |_ %s/%s does not exist on the target fabric. Skipping..." % (tn, bd))
            continue
        else:
            # Now we add all the GWs that we found on the input file. If they
            # already existed, we pull the existing object and update the 
            # parameters, just in case something like the scope changed.
            if sn not in bd_subnets:
                output(" |_ Subnet %s/%s/%s did not exist and will be added." % (tn, bd, sn))
                subnet = Subnet("", bd_obj)
                subnet.set_addr(sn)
                bd_obj.add_subnet(subnet)
                subnet.set_scope(scope)
            else:
                output(" |_ Subnet %s/%s/%s already exists on the fabric." % (tn, bd, sn))
                subnet = bd_subnets[sn]
                if subnet.get_scope() != scope:
                    subnet.set_scope(scope)
                    output("   |_ Subnet scope will be updated to '%s'" % scope)
            
            if bd_obj.get_unknown_mac_unicast() != flood_uni:
                bd_obj.set_unknown_mac_unicast(flood_uni)
                output("   |_ Unicast flooding will be updated to '%s'" % flood_uni)
            if bd_obj.get_unknown_multicast() != flood_multi:
                bd_obj.set_unknown_multicast(flood_multi)
                output("   |_ Multicast flooding will be updated to '%s'" % flood_uni)
            if bd_obj.get_arp_flood() != flood_arp:
                bd_obj.set_arp_flood(flood_arp)
                output("   |_ ARP flooding will be updated to '%s'" % flood_arp)
            if bd_obj.get_unicast_route() != do_routing:
                bd_obj.set_unicast_route(do_routing)
                output("   |_ Unicast routing will be updated to '%s'" % do_routing)
            if bd_obj.get_mac() != mac_addr:
                bd_obj.set_mac(mac_addr)
                output("   |_ MAC Address will be updated to '%s'" % mac_addr)

            # Add the tenant this BD belongs to to the list of tenants we need to
            # push (in case we had more existing tenants than the ones we really
            # need to make changes to)
            tenants_modified[tn] = existing_tenants[tn]['object']

    # Now if the user passed --remove this means we need to get rid of the
    # existing BD GWs (not the ones we've just created, but the ones that 
    # were already on the fabric). So here, we iterate through the list of 
    # existing GWs and we delete them if we have added a new GW to the same BD
    for t in existing_tenants:
        for b in  existing_tenants[t]['bds']:
            for s in existing_tenants[t]['bds'][b]['subnets']:
                if t in input_tenants:
                    if b in input_tenants[t]['bds']:
                        if s not in input_tenants[t]['bds'][b]['subnets']:
                            if args.remove == True:
                                print(" |_ Existing Subnet %s/%s/%s will be REMOVED from the fabric." % (t,b,s))
                                tn = existing_tenants[t]['object']
                                bd = existing_tenants[t]['bds'][b]['object']
                                sn = existing_tenants[t]['bds'][b]['subnets'][s]
                                
                                # Mark the subnet as deleted
                                sn.mark_as_deleted()
                                
                                # Add the corresponding subnet to the BD so 
                                # we can push it with the deleted status
                                bd.add_child(sn)
                            else:
                                print(" |_ Existing Subnet %s/%s/%s will be kept intact because no '--remove yes' was supplied." % (t,b,s))

    if args.commit == True:
        for tenant_name in tenants_modified:
            output("[+] Pushing configuration for Tenant '%s'" % tenant_name)
            tenant = tenants_modified[tenant_name]
            debug(tenant.get_json())
            r = session.push_to_apic(tenant.get_url(), data=tenant.get_json())
            if r.status_code>299:
                try:
                    resp_data = json.loads(r.text)
                    errmsg = resp_data['imdata'][0]['error']['attributes']['text']
                except:
                    errmsg = r.text
                fatal("[E] ERROR: %s" % errmsg)
            else:
                output("[+] Configuration for Tenant '%s' pushed successfully" % tenant_name)
    else:
        output("[+] No configuration pushed because '--commit yes' not supplied.")

    sys.exit(0)
