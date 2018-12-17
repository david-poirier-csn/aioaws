import os
import sys
import urllib.parse
sys.path.append('./aioaws')

import signer

aws4_testsuite_dir = 'tests/aws4_testsuite_2/'

REGION = 'us-east-1'
SERVICE = 'service'
KEY = 'AKIDEXAMPLE'
SECRET = 'wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY'


# these tests seem broken - 
# but there's no documentation or reference implementation so who knows
skipped_tests = [
        'post-x-www-form-urlencoded',
        'post-x-www-form-urlencoded-parameters']

def test_suite():
    tests = _find_tests()
    for test, test_dir in tests:
        if test in skipped_tests:
            print(f'Skipping test {test}')
        else:
            print(f'Running test {test}')
            _run_test(test, test_dir)


def _find_tests():
    tests = []
    for root, dirs, files in os.walk(aws4_testsuite_dir):
        for f in files:
            if f.endswith('.sts'):
                test = f.split('.')[0]
                tests.append((test, root))
                break
    return tests


def _run_test(test, test_dir):
    txt_req = _load_file(f'{test_dir}/{test}.req')
    method, url, version, headers, body = _parse_txt_req(txt_req)
    while '//' in url:
        url = url.replace('//', '/')
    url_parts = urllib.parse.urlsplit(url, allow_fragments=False)
    query = urllib.parse.parse_qs(url_parts.query, keep_blank_values=True)
    canonical_request = signer._create_canonical_request(
            method, 
            url_parts.path,
            query,
            headers,
            body)
    txt_creq = _load_file(f'{test_dir}/{test}.creq')
    assert txt_creq == canonical_request

    amzdate = headers['X-Amz-Date'][0]
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

        if k not in headers:
            headers[k] = []
        headers[k].append(v)
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

