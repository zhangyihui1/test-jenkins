# -*- coding: utf-8 -*-
import requests
from requests.auth import HTTPBasicAuth
import json
#url = "https://api.github.com" /repos/:owner/:repo/comments/:comment_id/reaction
url = "https://api.github.com/repos/zhangyihui1/test-jenkins/issues/1/comments"
headers = {"Authorization": " token 424e18e427fa5ea808fed8a40914e5bee69db87c"}

body = {"body": "text23"}
response = requests.post(url, data=json.dumps(body), auth=HTTPBasicAuth('zhangyihui1', 'zhang541207'))

print response.text
print response.status_code
