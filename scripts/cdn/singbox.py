import argparse
import json
import os
import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings()

parser = argparse.ArgumentParser()
parser.add_argument('--url1', help='Url1')
parser.add_argument('--url2', help='Url2')
parser.add_argument('--url3', help='Url3')
parser.add_argument('--url4', help='Url4')
args, unknown = parser.parse_known_args()

class Singbox:
    def fetch(self, url):
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception as e:
                data = {}
                print(f"JSON解析失败: {e}")
                print(f"完整响应内容: {response.text}")

        return data

    def save(self, dir, filename, data):
        os.makedirs(dir, exist_ok=True)
        with open(dir + filename, "w") as file:
            json.dump(data, file)

    def pc(self, res):
        data = json.loads(
            '{ }'
        )
        return {**data, **res}

    def mobile(self, res):
        data = json.loads(
            '{ "dns": { "servers": [{ "type": "tls", "server": "1.1.1.1", "detour": "out_proxy" }] }, "inbounds": [ { "type": "tun", "tag": "tun-in", "address": ["172.19.0.1/30"], "auto_route": true, "strict_route": false } ], "outbounds": [{ "tag": "out_direct", "type": "direct" }], "route": { "final": "out_proxy", "auto_detect_interface": true, "rules": [ { "action": "sniff" }, { "protocol": "dns", "action": "hijack-dns" }, { "ip_is_private": true, "outbound": "out_direct" }, { "rule_set": ["geoip-us"], "outbound": "out_proxy" }, { "rule_set": ["geoip-cn"], "outbound": "out_direct" } ], "rule_set": [ { "tag": "geoip-us", "type": "remote", "format": "binary", "url": "https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-us.srs", "download_detour": "out_proxy" }, { "tag": "geoip-cn", "type": "remote", "format": "binary", "url": "https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-cn.srs", "download_detour": "out_proxy" } ] } }'
        )
        res["outbounds"][0]["tag"] = 'out_proxy'
        data["outbounds"] = data["outbounds"] + res["outbounds"]
        return data

    def run(self):
        urls = {
            "config1.json": args.url1,
            "config2.json": args.url2,
            "config3.json": args.url3,
            "config4.json": args.url4,
        }
        for key, value in urls.items():
            try:
                res = self.fetch(value)
                self.save("./docs/singbox/pc/", key, self.pc(res))
                self.save("./docs/singbox/mobile/", key, self.mobile(res))
            except Exception as e:
                print(f"失败: {e}")
