import urllib.request
import json

data = json.dumps({'query': 'transformer architectures'}).encode('utf-8')
req = urllib.request.Request(
    'https://paper-search-agent-234338064518.us-central1.run.app/query',
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    response = urllib.request.urlopen(req, timeout=120)
    print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f'HTTP Error: {e.code}')
    print(e.read().decode())