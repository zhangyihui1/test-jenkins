import requests
import json
 
url = 'https://api.github.com/repos/zhangyihui1/test-jenkins/pulls/1/comments'
data_json = {
  "body": "Nice change",
  "commit_id": "873303e88575f93cbcc944f1c6a93b1b5ec4909b",
  "position": 1
}
headers = {'Accept': 'application/vnd.github.v3.diff'}

response = requests.post(url, data = json.dumps(data_json), headers = headers)

print response.text

print response.status_code
