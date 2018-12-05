################################################################################
#                                                                              #
# Copyright (c) 2016 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, this software  #
#    is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF   #
#    ANY KIND, either express or implied.                                      #
#                                                                              #
################################################################################


# list of packages that should be imported for this code to work
import sys
import cobra.mit.access
import cobra.mit.session
import cobra.mit.request
import cobra.mit.mo
import cobra.model.fv
import cobra.model.aaa
import cobra.model.vz
import cobra.model.pol
from cobra.internal.codec.xmlcodec import toXMLStr
from cobra.model.fv import Tenant
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def main(host, user, password, tenants, tenantprefix):

    # log into an APIC and create a directory object
    
    ls = cobra.mit.session.LoginSession('http://'+str(host), user, 'ins3965!')
    md = cobra.mit.access.MoDirectory(ls)
    md.login()
   
    ltenants = str(int(tenants)+1) 
    
# build the request using cobra syntax
  
    for x in range(1, int(ltenants)):
        # the top level object on which operations will be made
        topMo = cobra.model.pol.Uni('')
        tname = str(tenantprefix)+str(x)
        fvTenant = cobra.model.fv.Tenant(topMo, ownerKey='', name=tname, descr='', ownerTag='')
        tvrf=str(tname)+'-VRF'
        #Create VRF 
        fvCtx = cobra.model.fv.Ctx(fvTenant, ownerKey='', name=tvrf, descr='', knwMcastAct='permit', ownerTag='', pcEnfPref='unenforced')
       
        # Create BD        
        tbd=str(tname)+'-BD'
        fvBD = cobra.model.fv.BD(fvTenant, ownerKey='', name=tbd, descr='', unkMacUcastAct='proxy', arpFlood='yes',  unicastRoute='yes', ownerTag='', unkMcastAct='opt-flood')
        fvRsCtx = cobra.model.fv.RsCtx(fvBD, tnFvCtxName=tvrf)
        fvSubnet = cobra.model.fv.Subnet(fvBD, ip='10.10.'+str(x)+'.1/24', name='', descr='', ctrl='')
      
        # Create Application Profile 
        fvAp = cobra.model.fv.Ap(fvTenant, ownerKey='', prio='unspecified', name='APP', descr='', ownerTag='')
        
        #Create EPG's
        fvAEPg = cobra.model.fv.AEPg(fvAp, prio='unspecified', matchT='AtleastOne', name='EPG1', descr='')
        fvRsBd = cobra.model.fv.RsBd(fvAEPg, tnFvBDName=tbd)
        fvAEPg2 = cobra.model.fv.AEPg(fvAp, prio='unspecified', matchT='AtleastOne', name='EPG2', descr='')
        fvRsBd2 = cobra.model.fv.RsBd(fvAEPg2, tnFvBDName=tbd)
        

	# commit the generated code to APIC
        # print toXMLStr(topMo)
        c = cobra.mit.request.ConfigRequest()
        c.addMo(fvTenant)
        md.commit(c)

if __name__ == '__main__':
        from argparse import ArgumentParser
        parser = ArgumentParser("Tenant creation script")
        parser.add_argument('-d', '--host', help='APIC host name or IP',
                            required=True)
        parser.add_argument('-p', '--password', help='user password',
                            required=False)
        parser.add_argument('-u', '--user', help='user name', required=True)
        parser.add_argument('-t', '--tenants', help='Number of Tenants', required=True)
        parser.add_argument('-tp', '--tenantprefix', help=' Tenant Prefix', required=True)
        args = parser.parse_args()

        main(args.host, args.user, args.password, args.tenants, args.tenantprefix)
