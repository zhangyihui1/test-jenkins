import requests
import json
import sys
import os
import argparse
from datetime import datetime
from jwt import (
	JWT,
	jwk_from_dict,
	jwk_from_pem,
)

try:
	from cStringIO import StringIO
except ImportError:
	from io import StringIO

HOME_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG = json.loads(open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r').read())


def do_post(url, data, headers):
	response = requests.post(url, data=data, headers=headers)
	if response.status_code != 201:
		print(response.text)
		sys.exit(1)
	else:
		return response.text


def generate_jwt(apps_id, pem_file_name):
	utcnow = int(datetime.utcnow().timestamp())
	payload = {
		"iat": utcnow,
		"exp": utcnow + 29000,
		"iss": apps_id
	}
	with open(os.path.join(HOME_PATH, pem_file_name), 'rb') as fh:
		signing_key = jwk_from_pem(fh.read())
	return JWT().encode(payload, signing_key, 'RS256')


def generate_report(detail_msg):
	output = StringIO()
	device_model = detail_msg.get('deviceModel', None)
	device_version = detail_msg.get('deviceVersion', None)
	if device_model is not None and device_version is not None:
		output.write(
			'''<table><thead><tr><th>DEVICE MODEL</th><th>DEVICE VERSION</th>
			</tr></thead><tbody><tr>''')
		output.write('<td>' + device_model + '</td>')
		output.write('<td>' + device_version + '</td>')
		output.write('</tr></tbody></table>')
		
	output.write(
		'''<table><thead><tr><th>Total</th><th>Success</th>
		<th>Faliure</th></tr></thead><tbody><tr>''')
	output.write('<td>' + str(detail_msg.get('total', "0")) + '</td>')
	output.write('<td>' + str(detail_msg.get('success', "0")) + '</td>')
	output.write('<td>' + str(detail_msg.get('failure', "0")) + '</td>')
	output.write('</tr></tbody></table>')
	if detail_msg.get('errorDate', None) is not None:
		for error in detail_msg.get('errorDate', None):
			output.write('<b>Failed test case</b><br/>')
			output.write('<p>' + error.get('caseName', "None") + '</p>')
			output.write('<b>Case log</b><br/>')
			output.write('<pre>' + error.get('error', "None") + '</pre>')
	html = output.getvalue()
	output.close()
	return html


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('--owner', dest='owner', required=True,
	                    help='Github owner.')
	parser.add_argument('--repo', dest='repo', required=True,
	                    help='Github repo.')
	parser.add_argument('--commit-id', dest='commit_id', required=True,
	                    help='Commit id.')
	parser.add_argument('--error-report', dest='error_report', default=None,
	                    help='CI detail message.')
	args = parser.parse_args()

	if args.error_report is not None and os.path.exists(args.error_report):
		errors = json.loads(open(os.path.abspath(args.error_report), 'r').read())
	else:
		sys.exit(0)
	for detail_msg in errors:
		module = detail_msg.get('module', None)
		if module in CONFIG:
			headers  = {"Authorization": "Bearer " + generate_jwt(CONFIG[module]['appsId'], CONFIG[module]['pemFileName']),
	                "Accept": "application/vnd.github.machine-man-preview+json"
	              }
			url = "https://api.github.com/app/installations/" + str(CONFIG[module]['installationId']) + "/access_tokens"
			response = do_post(url=url, data=None, headers=headers)
		
			token = json.loads(response)['token']
		
			now = datetime.utcnow()
			format_iso_now = now.isoformat()
	
			url = "https://api.github.com/repos/" + args.owner + "/" + args.repo + "/check-runs"
			headers = {"Authorization": "token " + token,
	              "Accept": "application/vnd.github.antiope-preview+json"
		            }
			body = {
				"name": detail_msg["name"],
				"head_sha": args.commit_id,
				"status": "completed",
				"conclusion": "success",
				"completed_at": format_iso_now + "Z",
				"output": {
					"title": detail_msg['title'],
					"summary": generate_report(detail_msg)
				}
			}
			response = do_post(url=url, data=json.dumps(body), headers=headers)
			print(response)
