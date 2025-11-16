import requests
resp = requests.get('http://127.0.0.1:8000/openapi.json')
resp.raise_for_status()
data = resp.json()
for path, methods in data.get('paths', {}).items():
    print(path, '->', ','.join(methods.keys()))
