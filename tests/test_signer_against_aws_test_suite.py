import os
import sys
import urllib.parse
sys.path.append('./aioaws')

import signer

aws_test_suite_dir = 'tests/aws-sig-v4-test-suite/aws-sig-v4-test-suite/'

REGION = 'us-east-1'
SERVICE = 'service'
KEY = 'AKIDEXAMPLE'
SECRET = 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY'


def test_suite():
    tests = _find_tests()
    for test, test_dir in tests:
        if 'post-x-www-form-urlencoded' in test:
            print(f'Skipping test {test}')
        else:
            print(f'Running test {test}')
            _run_test(test, test_dir)


def _find_tests():
    tests = []
    for root, dirs, files in os.walk(aws_test_suite_dir):
        for f in files:
            if f.endswith('.req'):
                tests.append((root.split('/')[-1], root))
                break
    return tests


def _run_test(test, test_dir):
    txt_req = _load_file(f'{test_dir}/{test}.req')
    method, url, version, headers, body = _parse_txt_req(txt_req)
    while '//' in url:
        url = url.replace('//', '/')
    canonical_request = signer._create_canonical_request(
            method, 
            urllib.parse.urlsplit(url).path,
            urllib.parse.parse_qs(urllib.parse.urlsplit(url).query),
            headers,
            body)
    txt_creq = _load_file(f'{test_dir}/{test}.creq')
    assert txt_creq.encode() == canonical_request.encode()

    amzdate = headers['X-Amz-Date']
    datestamp = amzdate[:8]
    string_to_sign = signer._create_string_to_sign(
            amzdate, datestamp, REGION, SERVICE, canonical_request)
    txt_sts = _load_file(f'{test_dir}/{test}.sts')
    assert txt_sts == string_to_sign

    authorization_header = signer._create_authorization_header(
            KEY, SECRET, datestamp, REGION, SERVICE, headers, string_to_sign)
    txt_authz = _load_file(f'{test_dir}/{test}.authz')
    assert txt_authz == authorization_header


def _parse_txt_req(txt_req):
    lines = txt_req.split('\n')
    head = lines[0].split(' ')
    method = head[0]
    url = ' '.join(head[1:len(head)-1])
    version = head[-1]

    headers = {}
    i = 1
    while i < len(lines):
        line = lines[i]
        if line=='':
            break
        sep = line.find(':')
        k = line[:sep].strip()
        v = line[sep+1:].strip()

        while i+1 < len(lines):
            next_line = lines[i+1]
            if next_line.startswith(' ') or next_line.startswith('\t'):
                v += ',' + next_line.strip()
            else:
                break
            i += 1

        if k in headers:
            headers[k] += ',' + v
        else:
            headers[k] = v
        i += 1
    
    body = ''
    while i < len(lines):
        if body != '':
            body += '\r\n'
        body += lines[i]
        i += 1

    return method, url, version, headers, body


def _load_file(filename):
    with open(filename, 'r') as f:
        return f.read()

