#!/usr/bin/python3
'''
AWS DnyDNS. See README.md for further details
or github.com/yoloClin/aws-dnydns
'''
# pylint decides 'ip' is not a valid variable name
# pylint: disable=invalid-name

import os
import logging
import time
import json
from typing import Dict
from subprocess import Popen, PIPE
import requests

logging.basicConfig()
LOG = logging.getLogger("aws-dnydns")
LOG.setLevel(logging.INFO)


def get_templates(path_of_templates: str) -> Dict[str, str]:
    '''
    Returns all parsed zonefile templates
    '''
    templates = {}
    for i in os.listdir(path_of_templates):
        if not i.endswith(".zonefile-template"):
            continue
        key = i.split(".zonefile-template")[0]
        templates[key] = open(i).read()
    return templates


def update_ip(ip: str, path_of_templates: str) -> None:
    '''
    Actually triggers the DNS update from AWS
    '''
    templates = get_templates(path_of_templates)
    for domain, template in templates.items():
        if os.path.exists("/tmp/" + domain):
            os.remove("/tmp/" + domain)
        with open("/tmp/" + domain, "w") as fhandle:
            fhandle.write(template.format(ip=ip))
        proc = Popen(["/bin/cli53", "import",
                      "--file", "/tmp/" + domain,
                      "--replace", "--wait", domain],
                     stdout=PIPE, stderr=PIPE)
        out = proc.communicate()
        assert not out[1]
        assert b"records imported" in out[0]


def validate_ip(ip: str) -> None:
    '''
    Raises an exception if the IP address is not valid
    '''
    assert ip.count(".") == 3
    octets = ip.split(".")
    for octet in octets:
        octet = int(octet)
        assert octet >= 0 and octet <= 255


def mainloop(path_of_templates: str, timeout: int) -> None:
    '''
    Mainloop, triggers update_ip when IP changes or on first run
    '''
    last_ip = None
    LOG.info(json.dumps({"msg": "aws-dnydns starting", "ts": time.time()}))
    while True:
        itr_start = time.time()
        LOG.debug(json.dumps({"msg": "starting loop iteration",
                              "ts": time.time()}))
        response = requests.get("https://api.ipify.org")
        assert response.status_code == 200
        ip = response.content.decode()
        validate_ip(ip)
        if ip != last_ip:
            LOG.info(json.dumps({"msg": "IP changed", "ts": time.time(),
                                 "old": last_ip, "new": ip}))
            update_ip(ip, path_of_templates)
            last_ip = ip
        LOG.debug("iteration complete.")
        itr_end = time.time()
        sleep_time = timeout -  (itr_end - itr_start)
        if sleep_time > 0:
            LOG.debug("sleeping for %s seconds", sleep_time)
            time.sleep(sleep_time)


if __name__ == "__main__":
    assert get_templates("/zonefiles")
    mainloop("/zonefiles", 60)
