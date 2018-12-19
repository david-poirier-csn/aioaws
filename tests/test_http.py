import asyncio
import sys
sys.path.append('./aioaws')

import _http, request

def test_example():
    req = request.Request(
            method='GET',
            url='/',
            version='HTTP/1.1',
            headers={'Host': 'www.example.com'})
    resp = asyncio.run(_http.request(req))

    assert 200 == resp.status_code

