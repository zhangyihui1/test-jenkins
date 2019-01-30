import json
import re
from xml.dom import minidom
import os
import subprocess

GENERATE_CI_REPORT = [
	{
		"module": "p2p",
		"mode": "instrumentation",
		"name": "API test",
		"title": "Android-p2p-instrumentation-results",
		"report": "/home/fengwei/github_checks/p2p_result.txt"
	},
	{
		"module": "conference",
		"mode": "instrumentation",
		"name": "API test",
		"title": "Android-conference-instrumentation-results",
		"report": "/home/fengwei/github_checks/conference_result.txt"
	},
	{
		"module": "p2p",
		"mode": "unit",
		"name": "Unit test",
		"title": "Android-unit-p2p-results",
		"report": "/home/fengwei/github_checks/p2p-unit-result-1548754187.xml"
	}
]


# [
#  {
#    "name": "android[conferece]",
#    "title": "android-conference results",
#    "total": "5",
#    "success": "4",
#    "failure": "1",
#    "errorDate": [
#      {
#        "caseName": "test_conference_join",
#        "error": "1111111111111111"
#      }
#    ]
#  },
#  {
#    "name": "android[p2p]",
#    "title": "android-p2p results",
#    "total": "3",
#    "success": "3",
#    "failure": "0",
#    "errorDate": [
#      {
#        "caseName": "test_p2p_connect",
#        "error": "2222222222"
#      }
#    ]
#  }
# ]

def generate_report_by_unit(item):
	try:
		xml_doc = minidom.parse(item['report'])
	except:
		print("Error occured while reading test result.")
		return None
	failure_case_list = []
	report_data = {}
	report_data['module'] = item['module']
	report_data['name'] = item['name']
	report_data['title'] = item['title']
	
	test_suite = xml_doc.documentElement
	total_num = int(test_suite.attributes["tests"].value)
	failed_num = int(test_suite.attributes["failures"].value)
	error_num = int(test_suite.attributes["errors"].value)
	success_num = total_num - failed_num - error_num
	test_cases = test_suite.getElementsByTagName("testcase")
	for case in test_cases:
		failure_tag = case.getElementsByTagName('failure')
		if len(failure_tag) != 0:
			error_msg = failure_tag[0].childNodes[0].data.replace("\n", "\n\t").strip("\t")
			case_name = case.attributes["classname"].value
			failure_case_list.append({'caseName': case_name, 'error': error_msg})
	if len(failure_case_list) != 0:
		report_data['errorDate'] = failure_case_list
	report_data['total'] = total_num
	report_data['success'] = success_num
	report_data['failure'] = failed_num + error_num
	return report_data


def generate_report_by_instrumentation(item):
	if not os.path.exists(item['report']):
		return None
	failure_case_list = []
	ok_num = 0
	fail_num = 0
	with open(item['report'], 'r') as f:
		report_data = {}
		report_data['module'] = item['module']
		report_data['name'] = item['name']
		report_data['title'] = item['title']
		case_name = None
		status = ''
		error_msg = ''
		start_record = False
		for line in f:
			case_match = p.match(line)
			if start_record and status == "failure":
				if line.find('\n') == 0:
					failure_case_list.append({'caseName': case_name, 'error': error_msg})
					error_msg = ''
					start_record = False
				else:
					error_msg = error_msg + line
			if case_match is not None:
				case_name = case_match.group(1)
			elif line.find('INSTRUMENTATION_RESULT: shortMsg=') == 0:
				status = "crash"
				fail_num += 1
				start_record = True
			elif line.find('INSTRUMENTATION_STATUS: stack=') == 0:
				status = "failure"
				error_msg = error_msg + line
				fail_num += 1
				start_record = True
			elif line.find('OK (1 test)') == 0:
				ok_num += 1
			if start_record and status == 'crash':
				error_msg = line
				failure_case_list.append({'caseName': case_name, 'error': error_msg})
				error_msg = ''
				start_record = False
		total_num = ok_num + fail_num
		if len(failure_case_list) != 0:
			report_data['errorDate'] = failure_case_list
		report_data['total'] = total_num
		report_data['success'] = ok_num
		report_data['failure'] = fail_num
	return report_data


def get_device(device):
	device_model = None
	device_version = None
	adb = ['adb'] if device == None else ['adb', '-s', device]
	cmd = ['shell', 'getprop']
	stdout, stderr = subprocess.Popen(adb + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
	for item in bytes.decode(stdout).split('\n'):
		if item.find('ro.product.model') != -1:
			device_model = re.split(':\s+',item)[1].lstrip('[').rstrip(']')
		elif item.find('ro.build.version.release') != -1:
			device_version = re.split(':\s+',item)[1].lstrip('[').rstrip(']')
		
		if device_model is not None and device_version is not None:
			break
	return device_model, device_version
	

if __name__ == '__main__':
	device_model, device_version = get_device(None)
	report_list = []
	report_item = None
	p = re.compile(r'INSTRUMENTATION_STATUS: test=(\w*)')
	for item in GENERATE_CI_REPORT:
		if item['mode'] == 'instrumentation':
			report_item = generate_report_by_instrumentation(item)
		elif item['mode'] == 'unit':
			report_item = generate_report_by_unit(item)
		if report_item is not None:
			report_item['deviceModel'] = device_model
			report_item['deviceVersion'] = device_version
			report_list.append(report_item)
	with open('test_result.json', 'w') as f:
		json.dump(report_list, f, indent=4)
