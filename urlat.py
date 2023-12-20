#!/usr/bin/env python

from argparse import ArgumentParser
import re
import ipaddress
import random
import string
import socket
import time
import dns.resolver
import base64
from urllib.parse import quote, urlparse

class Color:
    ok_b = '\033[94m'
    ok_cy = '\033[96m'
    warn = '\033[93m'
    fail = '\033[91m'
    reset = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'

banner = f"""

{Color.fail}

 █    ██  ██▀███   ██▓        ▄▄▄     ▄▄▄█████▓
 ██  ▓██▒▓██ ▒ ██▒▓██▒       ▒████▄   ▓  ██▒ ▓▒
▓██  ▒██░▓██ ░▄█ ▒▒██░       ▒██  ▀█▄ ▒ ▓██░ ▒░
▓▓█  ░██░▒██▀▀█▄  ▒██░       ░██▄▄▄▄██░ ▓██▓ ░ 
▒▒█████▓ ░██▓ ▒██▒░██████▒    ▓█   ▓██▒ ▒██▒ ░ 
░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░░ ▒░▓  ░    ▒▒   ▓▒█░ ▒ ░░   
░░▒░ ░ ░   ░▒ ░ ▒░░ ░ ▒  ░     ▒   ▒▒ ░   ░    
 ░░░ ░ ░   ░░   ░   ░ ░        ░   ▒    ░      
   ░        ░         ░  ░         ░  ░

{Color.reset}

"""

# Set seed
random.seed(time.time())

def get_args():
    parser = ArgumentParser(description='IP Mutation Script that craft URL links with @ redirect')
    parser.add_argument('-i', '--ip', help='Redirect Destination IP to perform mutation on')
    parser.add_argument('-s', '--schema', help='URL to spoof (e.g., site.com)')
    parser.add_argument('-p', '--path', help='Redirect Destination URL path (optional)', default='')
    parser.add_argument('-sp', '--schema-path', help='URL arguments after the TLD to perform encoding on')
    parser.add_argument('-r', '--rand-url', action='store_true', help='Use random URL')
    parser.add_argument('-d', '--domain', help='Domain to retrieve IP from')
    parser.add_argument('-f', '--fake-slash', action='store_true', help='Replace slashes in schema or schema-path with unicode char U+2215')
    parser.add_argument('-e', '--encode', action='store_true', help='Encode the final URL - the sp parameter is base64 encoded while the rest is url encoded')
    return parser.parse_args()

def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def retrieve_ip_from_domain(domain):
    try:
        answers = dns.resolver.resolve(domain, 'A')
        ip = answers[0].address
        return ip
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout):
        return None

randbase_values = []

def generate_random_schema():
    schema = ''
    for _ in range(8):
        # Add 4-9 lowercase letters
        schema += ''.join(random.choice(string.ascii_lowercase) for _ in range(random.randint(4, 9)))
        # Add 5-8 zeroes
        schema += '0' * random.randint(5, 8)
    return schema

def print_output(ip):
    global randbase_values
    parts = ip.split('.')

    decimal = int.from_bytes(socket.inet_aton(ip), byteorder='big')
    print("")

    print(f"{Color.bold}IP Decimal form:{Color.reset}\t{Color.underline}{decimal}{Color.reset}")
    print(f"{Color.bold}IP Hexadecimal form:{Color.reset}\t{Color.underline}{hex(decimal)}{Color.reset}")
    print(f"{Color.bold}IP Octal form:{Color.reset}\t\t{Color.underline}{oct(decimal)}{Color.reset}")

    print("")

    print(f"{Color.bold}Full Hex:{Color.reset}\t{Color.underline}{'.'.join([hex(int(i)) for i in parts])}{Color.reset}")
    print(f"{Color.bold}Full Oct:{Color.reset}\t{Color.underline}{'.'.join([oct(int(i)) for i in parts])}{Color.reset}")

    randbase_values = generate_randbase_values(parts)

def generate_randbase_values(parts):
    randbase_values = []
    for _ in range(5):
        randbaseval = ""
        for i in range(4):
            randbaseval += random_value(parts[i]) + '.'
        randbase_values.append(randbaseval[:-1])
    return randbase_values

def random_value(part):
    val = random.randint(0, 2)
    if val == 0:
        return part
    elif val == 1:
        return hex(int(part))
    else:
        return oct(int(part))

def print_url_with_schema(ip, schema, randbase_values, path='', schema_path=None):
    args = get_args()

    if schema == 'random':
        schema = generate_random_schema()

    if args.fake_slash:
        schema = schema.replace('/', '\u2215')
        if schema_path and args.fake_slash:
            schema_path = schema_path.replace('/', '\u2215')

    encoded_schema = encode_schema(schema)
    joined_hexparts = '.'.join([hex(int(i)) for i in ip.split('.')])
    joined_octparts = '.'.join([oct(int(i)) for i in ip.split('.')])

    print_standard_url(ip, encoded_schema, joined_hexparts, joined_octparts, path, schema_path)
    print_random_base_urls(encoded_schema, randbase_values, path, args.encode, schema_path)

    if args.encode and schema_path is not None:
        print_encoded_base64_schema_path(encoded_schema, schema_path, joined_hexparts, joined_octparts, path, args.encode, randbase_values)

def encode_schema(schema):
    # Encode the schema part
    return quote(schema, safe='')

def print_standard_url(ip, encoded_schema, joined_hexparts, joined_octparts, path, schema_path=None):
    decimal = int.from_bytes(socket.inet_aton(ip), byteorder='big')

    print(f"\n{Color.bold}URL with User-Info {Color.reset} ==> {Color.warn}{encoded_schema}{Color.reset}")
    print("")
    print(f"{Color.bold}Decimal:{Color.reset}\t{Color.ok_b}https://{encoded_schema}{schema_path}@{decimal}{path}{Color.reset}")
    print(f"{Color.bold}Hex:{Color.reset}\t\t{Color.ok_b}https://{encoded_schema}{schema_path}@{joined_hexparts}{path}{Color.reset}")
    print(f"{Color.bold}Oct:{Color.reset}\t\t{Color.ok_b}https://{encoded_schema}{schema_path}@{joined_octparts}{path}{Color.reset}")
    print("")

def print_random_base_urls(encoded_schema, randbase_values, path, encode, schema_path=None):
    for i, randbase_value in enumerate(randbase_values):
        randbase_url = f"{encoded_schema}"
        encoded_randbase_url = quote(randbase_url, safe='') if encode else randbase_url
        print(f"{Color.bold}mixed #{i + 1}:{Color.reset}\t{Color.ok_b}https://{encoded_randbase_url}{schema_path}@{randbase_value}{path}{Color.reset}")

def print_encoded_base64_schema_path(encoded_schema, schema_path, joined_hexparts, joined_octparts, path, encode, randbase_values):
    encoded_schema_path = base64.urlsafe_b64encode(schema_path.encode()).decode()
    print(f"\n{Color.bold}Encoded Base64 User-Info Path:{Color.reset}")
    print(f"Encoded Path ==> {Color.warn}{encoded_schema_path}{Color.reset}")
    print("")

    for i, randbase_value in enumerate(randbase_values):
        randbase_url = f"{encoded_schema}"
        encoded_randbase_url = quote(randbase_url, safe='') if encode else randbase_url
        print(f"{Color.bold}mixed #{i + 1}:{Color.reset}\t{Color.ok_b}https://{encoded_schema}%20{encoded_schema_path}%7F%7F@{randbase_value}{path}{Color.reset}")

def main():
    print (banner)
    args = get_args()

    if args.ip:
        ip = args.ip
    elif args.domain:
        ip = retrieve_ip_from_domain(args.domain)
        if not ip:
            print(f"{Color.fail}[!] Unable to retrieve IP for domain: {args.domain}{Color.reset}")
            return
    else:
        print(f"{Color.fail}[!] Please provide either an IP or a domain.{Color.reset}")
        return

    if is_valid_ip(ip):
        print_output(ip)

        print("")
        print("")
        print(f"{Color.bold}IP Address {Color.reset} ==> {Color.warn}{ip}{Color.reset}")
        print(f"{Color.bold}Domain IP {Color.reset} ==> {Color.warn}{ip}{Color.reset}" if args.domain else "")
        # Pass schema_path as an argument
        print_url_with_schema(ip, args.schema if not args.rand_url else 'random', randbase_values, args.path, args.schema_path)
    else:
        print(f"{Color.fail}[!] Invalid IP format: {ip}{Color.reset}")

if __name__ == '__main__':
    main()
