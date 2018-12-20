import asyncio
import base64
import hashlib
import sys
sys.path.append('./aioaws')

import client, credentials, request

def test_s3():
    req = request.Request(
            method='GET',
            url='/dummy.txt',
            version='HTTP/1.1',
            headers={
                'Host': 'pxcrush-scratch.s3.amazonaws.com',
                'x-amz-content-sha256': hashlib.sha256(''.encode('utf-8')).hexdigest()
                })
    creds = credentials.Credentials()
    resp = asyncio.run(client.request(req, 'us-east-1', 's3', creds))

    assert 200 == resp.status_code


def test_rekognition():
    with open('tests/images/car.jpg', 'rb') as f:
        image = base64.b64encode(f.read()).decode('ascii')

    req = request.Request(
            method='POST',
            url='/',
            version='HTTP/1.1',
            headers={
                'Host': 'rekognition.us-east-1.amazonaws.com',
                'Content-Type': 'application/x-amz-json-1.1',
                'X-Amz-Target': 'RekognitionService.DetectLabels'
                },
            body={'Image': {'Bytes': image}})
    creds = credentials.Credentials()
    resp = asyncio.run(client.request(req, 'us-east-1', 'rekognition', creds))

    assert 200 == resp.status_code
