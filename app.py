import bisect
import json
from typing import List

import cherrypy


cherrypy.config.update('./server.ini')


def ip_to_int(ip: str) -> int:
    parts = ip.split('.')
    return int(parts[0]) * 16777216 + int(parts[1]) * 65536 + int(parts[2]) * 256 + int(parts[3])


ip_list: List[int] = []
country_list: List[str] = []
csv_file = cherrypy.config.get('iptoasn-country-ipv4.file')
with open(csv_file) as f:
    prev_int_ip: int = -1
    while s := f.readline():
        try:
            start_ip, end_ip, country = s[:-1].split(',')
            int_ip: int = ip_to_int(start_ip)
            if prev_int_ip != int_ip - 1:
                # add dummy for "not global" ip
                print(f'add:{start_ip}')
                ip_list.append(prev_int_ip + 1)
                country_list.append('--')

            ip_list.append(int_ip)
            country_list.append(country)
            prev_int_ip = ip_to_int(end_ip)
        except Exception as ex:
            print(ex)


def find_country_by_ip(ip_address: str) -> str:
    try:
        ipv4int: int = ip_to_int(ip_address)
        pos = bisect.bisect_right(ip_list, ipv4int) - 1
        return country_list[pos]
    except Exception as ex:
        print(ex)
        return ''


class ASN(object):
    @cherrypy.expose
    def index(self):
        return "OK"

    @cherrypy.expose
    def country(self):
        raw_data = cherrypy.request.body.read(int(cherrypy.request.headers['Content-Length']))
        request_json = json.loads(raw_data)
        ip: str = request_json.get('ip') or ''
        return json.dumps({'country': find_country_by_ip(ip)})


cherrypy.quickstart(ASN())
