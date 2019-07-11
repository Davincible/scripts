#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

    Date: July 11th, 2019
    Written by David Brouwer
    GitHub: https://github.com/davincible

    Script to check public ip, ip location, and if VPN is turned on
    put your API key for https://geo.ipify.org/ in key.txt:

    API_KEY_GEO_LOCATION=<API key>
    PUBLIC_IP=<public IP>  # optional

"""
import argparse
import json
import requests
from os.path import exists


def get_public_ip():
    print("Retrieving ip...")
    url = "https://api.ipify.org/?format=json"
    try:
        response = requests.get(url)

        if response.status_code == 200:
            response = response.text
            ip = json.loads(response)['ip']

            return_value = ip
        else:
            return_value = f"ERROR: request failed with error code {response.status_code}"
    except requests.exceptions.ConnectionError:
        return_value = "ERROR: connection error, check internet connection"

    return return_value


def get_ip_location(ip):
    file_name = 'keys.txt'
    key_name = 'API_KEY_GEO_LOCATION'
    public_ip_name = 'PUBLIC_IP'  # if PUBLIC_IP is saved in key.txt, compare against current ip to check if VPN is on
    api_key = None
    public_ip = None
    return_value = None

    if exists(file_name):
        with open(file_name, 'r') as file:
            for line in file.readlines():
                if key_name in line:
                    api_key = line.strip().split('=')[1]
                if public_ip_name in line:
                    public_ip = line.strip().split('=')[1]

        if api_key:
            print("Retrieving location...")
            url = f"https://geo.ipify.org/api/v1?apiKey={api_key}&ipAddress={ip}"
            response = requests.get(url)

            if response.status_code == 200:
                response = response.text
                location = json.loads(response)['location']
                location['public_ip'] = public_ip

                return_value = location
        else:
            return_value = "ERROR: failed to extract API key from key.txt"
    else:
        return_value = "ERROR: no key.txt file found"

    return return_value


def main():
    description = "Find your public ip and geolocation, or find geolocation by ip"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--ip', help="ip to look up geolocation")
    args = parser.parse_args()

    ip = args.ip if args.ip else get_public_ip()

    if "ERROR" not in ip:
        location = get_ip_location(ip)
        print("\nPublic ip", ip)
        if isinstance(location, dict):
            if location['public_ip'] and not args.ip:
                print("VPN turned on:", ip != location['public_ip'])
            print("Country:", location['country'])
            print("Region:", location['region'])
            print("City:", location['city'])
        else:
            print(location)
    else:
        print(ip)


if __name__ == '__main__':
    main()
