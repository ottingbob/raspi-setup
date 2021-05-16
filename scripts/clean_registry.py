
import requests
import sys
from typing import List
from dotenv import dotenv_values

# GET FROM ENV FILE
config = dotenv_values("env/.env")
host = config['REGISTRY_HOST']
port = config['REGISTRY_PORT']
base_registry_url = f'https://{host}:{port}/v2'
CONTENT_DIGEST_HEADER = 'Docker-Content-Digest'

resp = requests.get(f'{base_registry_url}/_catalog', verify=False)
if resp.status_code != 200:
    print("Unable to query docker registy catalog")
    sys.exit(1)

registry_catalog = resp.json()
repos = registry_catalog['repositories']


def get_tags_list(repo_name: str) -> List[str]:
    resp = requests.get(f'{base_registry_url}/{repo_name}/tags/list',
                        verify=False)
    if resp.status_code != 200:
        print("Unable to query docker registry tags for repo ", repo_name)
        return []
    return resp.json()['tags']


for repo in repos:
    accept_header = 'application/vnd.docker.distribution.manifest.v2+json'
    base_headers = {'Accept': accept_header}
    tags = get_tags_list(repo)
    for tag in tags:
        headers = requests.get(f'{base_registry_url}/{repo}/manifests/{tag}',
                               headers=base_headers,
                               verify=False).headers
        print("doing things...", headers)
        if CONTENT_DIGEST_HEADER in headers:
            digest = headers[CONTENT_DIGEST_HEADER]
            resp = requests.delete(f'{base_registry_url}/{repo}/manifests/{digest}',
                                   verify=False)
            print(resp.status_code)
            print(resp.json())
