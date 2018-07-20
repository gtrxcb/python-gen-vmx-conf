'''
Generate one or more Juniper vMX configuration files based on a input
YAML configuration file.

Version: 0.1
Written By: gtrxcb
'''

import os
import argparse
import random
import yaml
from jinja2 import Template

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def gen_mac():
    '''
    Generate a random MAC address based on the LAA (locally Administered Addresses) range.
    x2-xx-xx-xx-xx-xx --> Only currently supported range.
    x6-xx-xx-xx-xx-xx --> Not currently supported.
    xA-xx-xx-xx-xx-xx --> Not currently supported.
    xE-xx-xx-xx-xx-xx --> Not currently supported.
    '''

    HEX_VALUES = [f'{hex(i).lstrip("0x")}' for i in range(1, 16, 1)]
    mac_address = list()
    for i in range(0, 10, 1):
        mac_address.append(random.choice(HEX_VALUES).lower())
    mac_address = ''.join(mac_address)
    mac_address = ':'.join([mac_address[i:i+2] for i in range(0, len(mac_address), 2)]).lower()
    mac_address = f'02:{mac_address}'

    return mac_address


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', help='Configuration file')
    parser.add_argument('-t', '--template', help='Jinja Template file')
    args = parser.parse_args()

    if not args.config and not args.template:
        print(f'Usage: {__file__} -h')
    else:
        with open(file=args.config, mode='r') as f:
            config_data = yaml.load(f.read())

        for router in config_data['routers']:
            router['re_image'] = os.path.join(router['base_path'], router['hostname'], 'images', router['re_image'])
            router['re_hdd'] = os.path.join(router['base_path'], router['hostname'], 'images', router['re_hdd'])
            router['pfe_image'] = os.path.join(router['base_path'], router['hostname'], 'images', router['pfe_image'])

            router['re_mac'] = f'"{gen_mac()}"'
            router['pfe_mac'] = f'"{gen_mac()}"'

            ifaces_list = list()
            for iface in range(0, router['num_ifaces'], 1):
                iface_name = f'ge-0/0/{iface}'
                iface_mac = f'"{gen_mac()}"'
                iface_description = f'"ge-0/0/{iface} interface"'
                iface_dict = {'iface_entry': [iface_name, iface_mac, iface_description]}
                ifaces_list.append(iface_dict)

            router['interfaces'] = ifaces_list

            with open(file=args.template, mode='r') as f_template:
                template = f_template.read()
                t = Template(template)
                t_render = t.render(router)

            out_file = f'{router["hostname"]}.conf'
            with open(file=out_file, mode='w') as f_template:
                f_template.write(t_render)

            print(f'Generated {out_file} configuration.')


if __name__ == '__main__':
    main()
