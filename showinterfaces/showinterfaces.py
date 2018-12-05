import sys
import re
import json
import acitoolkit.acitoolkit as aci


def main():
    """
    Main execution routine
    :return: None
    """
    # Take login credentials from the command line if provided
    # Otherwise, take them from your environment variables file ~/.profile
    description = 'Simple application that logs on to the APIC and displays all of the Interfaces.'
    creds = aci.Credentials('apic', description)
    args = creds.get()

    # Login to APIC
    session = aci.Session(args.url, args.login, args.password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)

    resp = session.get('/api/class/ipv4Addr.json')
    intfs = json.loads(resp.text)['imdata']
    data = {}

    for i in intfs:
        ip = i['ipv4Addr']['attributes']['addr']
        op = i['ipv4Addr']['attributes']['operSt']
        cfg = i['ipv4Addr']['attributes']['operStQual']
        dn = i['ipv4Addr']['attributes']['dn']
        node = dn.split('/')[2]
        intf = re.split(r'\[|\]', dn)[1]
        vrf = re.split(r'/|dom-', dn)[7]
        if vrf not in data.keys():
            data[vrf] = []
        else:
            data[vrf].append((node, intf, ip, cfg, op))

    for k in data.keys():
        header = 'IP Interface Status for VRF "{}"'.format(k)
        print header
        template = "{0:15} {1:10} {2:20} {3:8} {4:10}"
        print(template.format("Node", "Interface", "IP Address ", "Admin Status", "Status"))
        for rec in sorted(data[k]):
            print(template.format(*rec))

if __name__ == '__main__':
    main()

