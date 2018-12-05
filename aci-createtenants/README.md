
    
                  == Create Multiple Tenants ==


Introduction
=============
ACI Create Tenants is a simple script to Create multiple tenats with one application profile and two EPGS.

Requirements
=============
- Python 2.7  or above.
- ACI Cobra SDK 

Usage
=====

The application  takes the regular parameters for APIC address, username and number of Tenants abd Tenant Prefix 

    host="192.168.0.90"
    user="admin"
    tenants=1
    tenantprefix="XYZ-1"


Usage Examples
==============

    $ python CreateTenants.py -h 192.168.0.90 -u "admin" -t 1 -tp "XYZ-1"


