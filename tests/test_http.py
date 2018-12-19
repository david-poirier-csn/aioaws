import asyncio
import sys
sys.path.append('./aioaws')

import _http, request

'''
def test_basic_request():
    req = request.Request(
            method='GET',
            url='/',
            version='HTTP/1.1',
            headers={'Host': ['www.google.com.au']})
    print(req._get_head_text())
    resp = asyncio.run(_http.request(req))
    print(resp.text())

    assert 200 == resp.status_code
'''
