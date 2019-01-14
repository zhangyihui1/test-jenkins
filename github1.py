import requests
import re
import json
from bs4 import BeautifulSoup
session = requests.Session()

def getToken():
    html = session.get('https://github.com/login')
    soup = BeautifulSoup(html.content, features="html.parser")
    return soup.find_all("input", attrs={"name": "authenticity_token"})[0].get("value")

def userpwdLogin():
    payload = {'login': 'zhangyihui1',
               'password': 'zhang541207',
               'authenticity_token': getToken()
               }
    r = session.post('https://github.com/session', data=payload)
    print r.status_code
    with open("test.html", 'w') as f:
        f.write(r.content)

        
userpwdLogin()
