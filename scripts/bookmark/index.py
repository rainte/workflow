import argparse
import json
import os
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--token', required=True, help='GitHub Token')
args, unknown = parser.parse_known_args()

url = "https://api.github.com/gists/c98539edb1fb4685b7ec8338358480ea"
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {args.token}",
}

response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

data = response.json()
content = json.loads(data["files"]["bookmark.json"]["content"])
res = content["children"][::-1]

with open("./docs/bookmark.json", "w") as file:
    os.makedirs("./docs/", exist_ok=True)
    json.dump(res, file)
