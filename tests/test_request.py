import json
import sys
sys.path.append('./aioaws')

import request

def test_basic_get():
    req = request.Request(
            method='GET',
            url='/',
            version='HTTP/1.1',
            headers={'Host': 'www.google.com.au'})

    assert 'GET / HTTP/1.1\r\nHost:www.google.com.au\r\n\r\n' == req._get_head_text()


def test_basic_post():
    req = request.Request(
            method='POST',
            url='/',
            version='HTTP/1.1',
            headers={
                'Host': 'www.google.com.au',
                'Content-Type': 'application/json'},
            body={'Key': 'Value'})

    assert 'POST / HTTP/1.1\r\nHost:www.google.com.au\r\nContent-Type:application/json\r\n\r\n' == req._get_head_text()
    assert '{"Key": "Value"}' == req._get_body_text()

