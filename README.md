## Async Python client for AWS services with no dependencies

### Usage

```python
from import client, credentials, request

req = request.Request(
        method='GET',
        url='/dummy.txt',
        version='HTTP/1.1',
        headers={
            'Host': 'dummy.s3.amazonaws.com',
            'x-amz-content-sha256': hashlib.sha256(''.encode('utf-8')).hexdigest()
        })
creds = credentials.Credentials()
resp = asyncio.run(client.request(req, 'us-east-1', 's3', creds))
```

