import json
import os
from pathlib import Path
from urllib.request import urlopen

BASE_CONFIG = {
  "dns": {
    "servers": [
      {
        "type": "tls",
        "tag": "dns-proxy",
        "server": "1.1.1.1",
        "detour": "proxy"
      }
    ]
  },
  "inbounds": [],
  "outbounds": [],
  "http_clients": [{ "tag": "downloader", "detour": "proxy" }],
  "route": {
    "final": "proxy",
    "auto_detect_interface": True,
    "default_http_client": "downloader",
    "rules": [
      { "action": "sniff" },
      { "protocol": "dns", "action": "hijack-dns" },
      { "ip_is_private": True, "outbound": "direct" },
      { "rule_set": ["geoip-us"], "outbound": "proxy" },
      { "rule_set": ["geoip-cn"], "outbound": "direct" }
    ],
    "rule_set": [
      {
        "tag": "geoip-us",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-us.srs"
      },
      {
        "tag": "geoip-cn",
        "type": "remote",
        "format": "binary",
        "url": "https://raw.githubusercontent.com/SagerNet/sing-geoip/rule-set/geoip-cn.srs"
      }
    ]
  }
}

PC_INBOUNDS = [
    {
        "type": "mixed",
        "tag": "mixed-in",
        "listen": "0.0.0.0",
        "listen_port": 1080,
        "set_system_proxy": False
    }
]

MOBILE_INBOUNDS = [
    {
        "type": "tun",
        "tag": "tun-in",
        "address": ["172.19.0.1/30"],
        "auto_route": True,
        "strict_route": False
    }
]

URL_KEYS = [f"SINGBOX_URL{i}" for i in range(1, 5)]


class Singbox:
    def fetch(self, url: str) -> dict:
        with urlopen(url, timeout=30) as resp:
            return json.load(resp)

    def build(self, res: dict, inbounds: list) -> dict:
        outbounds = [dict(o) for o in res["outbounds"]]
        outbounds[0]["tag"] = "proxy"
        return {**BASE_CONFIG, "inbounds": inbounds, "outbounds": outbounds}

    def pc(self, res: dict) -> dict:
        return self.build(res, PC_INBOUNDS)

    def mobile(self, res: dict) -> dict:
        return self.build(res, MOBILE_INBOUNDS)

    def mutate(self, work: Path) -> None:
        urls = {f"config{i}.json": os.environ.get(k) for i, k in enumerate(URL_KEYS, 1)}
        urls = {name: url for name, url in urls.items() if url}
        if not urls:
            raise RuntimeError("检查配置 URL1~URL4.")

        for name, url in urls.items():
            res = self.fetch(url)
            for kind, transform in (("pc", self.pc), ("mobile", self.mobile)):
                out = work / "docs" / "singbox" / kind / name
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(json.dumps(transform(res)), encoding="utf-8")
